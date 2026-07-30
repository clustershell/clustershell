# ClusterShell test suite
# Written by S. Thiell

"""Unit test for ClusterShell library logging"""

import logging
import sys
import unittest

from io import StringIO

import ClusterShell  # importing the package installs the NullHandler


class LibraryLoggingTest(unittest.TestCase):
    """Test the library logging posture (Python Logging HOWTO)"""

    def setUp(self):
        """save root logging state, other tests may have configured it"""
        self.saved_handlers = logging.root.handlers[:]
        self.saved_level = logging.root.level
        self.saved_stderr = sys.stderr
        logging.root.handlers[:] = []
        logging.root.setLevel(logging.WARNING)
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stderr = self.saved_stderr
        logging.root.handlers[:] = self.saved_handlers
        logging.root.setLevel(self.saved_level)

    def test_null_handler(self):
        """test NullHandler on the top-level ClusterShell logger"""
        handlers = logging.getLogger('ClusterShell').handlers
        self.assertTrue(any(isinstance(handler, logging.NullHandler)
                            for handler in handlers))

    def test_quiet_when_unconfigured(self):
        """test library logging is quiet when the application is not set up"""
        logging.getLogger('ClusterShell.Test').warning('should not be seen')
        self.assertEqual(sys.stderr.getvalue(), '')

    def test_propagate_when_configured(self):
        """test library records still reach application handlers"""
        stream = StringIO()
        logging.root.addHandler(logging.StreamHandler(stream))

        logging.getLogger('ClusterShell.Test').warning('should be seen')
        self.assertEqual(stream.getvalue(), 'should be seen\n')
