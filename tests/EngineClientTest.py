"""
Unit test for EngineClient line-buffered reads
"""

import unittest

from ClusterShell.Worker.EngineClient import EngineClient, \
    EngineClientStreamDict


class EngineClientReadlinesTest(unittest.TestCase):
    """test _readlines() line splitting and buffering"""

    def setUp(self):
        self.client = EngineClient.__new__(EngineClient)
        self.client.streams = EngineClientStreamDict()
        self.client.streams.set_stream('stdout')

    def readlines(self, chunk):
        """run _readlines() over a single input chunk"""
        self.client._read = lambda sname: chunk
        return list(self.client._readlines('stdout'))

    def rbuf(self):
        return self.client.streams['stdout'].rbuf

    def test_partial_line(self):
        """test _readlines() partial line buffering across chunks"""
        self.assertEqual(self.readlines(b'foo\nbar'), [b'foo'])
        self.assertEqual(self.rbuf(), b'bar')
        self.assertEqual(self.readlines(b'baz\n'), [b'barbaz'])
        self.assertEqual(self.rbuf(), b'')

    def test_crlf_split_across_chunks(self):
        """test _readlines() with CRLF split across two chunks"""
        self.assertEqual(self.readlines(b'foo\r'), [])
        self.assertEqual(self.rbuf(), b'foo\r')
        self.assertEqual(self.readlines(b'\nbar\n'), [b'foo', b'bar'])
        self.assertEqual(self.rbuf(), b'')

    def test_bare_cr_across_chunks(self):
        """test _readlines() buffers bare CR data across chunks"""
        self.assertEqual(self.readlines(b'a\rb\r'), [])
        self.assertEqual(self.rbuf(), b'a\rb\r')
        self.assertEqual(self.readlines(b'c\nrest'), [b'a\rb\rc'])
        self.assertEqual(self.rbuf(), b'rest')

    def test_double_cr_before_lf(self):
        """test _readlines() trims only the final CR of a CRLF"""
        self.assertEqual(self.readlines(b'foo\r\r\n'), [b'foo\r'])
        self.assertEqual(self.rbuf(), b'')
