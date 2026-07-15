"""
Unit test for ClusterShell.Gateway
"""

import base64
import logging
import os
import re
import select
import unittest
import xml.sax

from ClusterShell import __version__
from ClusterShell.Communication import ConfigurationMessage, ControlMessage, \
    StdOutMessage, StdErrMessage, RetcodeMessage, ACKMessage, ErrorMessage, \
    TimeoutMessage, StartMessage, EndMessage, XMLReader
from ClusterShell.Gateway import GatewayChannel
from ClusterShell.NodeSet import NodeSet
from ClusterShell.Propagation import PropagationChannel
from ClusterShell.Task import Task, task_self
from ClusterShell.Topology import TopologyError, TopologyGraph
from ClusterShell.Worker.Tree import TreeWorker
from ClusterShell.Worker.Worker import StreamWorker

from .TLib import HOSTNAME

# enable live DEBUG logging when running the tests
logging.basicConfig(level=logging.DEBUG)

# max time (secs) to wait for a gateway reply before failing the test
RECV_TIMEOUT = 30


class Gateway(object):
    """Gateway special test class.

    Initialize a GatewayChannel through a R/W StreamWorker like a real
    remote ClusterShell Gateway but:
        - using pipes to communicate,
        - running on a dedicated task/thread.
    """

    def __init__(self):
        """init Gateway bound objects"""
        self.task = Task()
        self.channel = GatewayChannel(self.task)
        self.worker = StreamWorker(handler=self.channel)
        # create communication pipes
        self.pipe_stdin = os.pipe()
        self.pipe_stdout = os.pipe()
        # avoid nonblocking flag as we want recv/read() to block
        self.worker.set_reader(self.channel.SNAME_READER,
                               self.pipe_stdin[0])
        self.worker.set_writer(self.channel.SNAME_WRITER,
                               self.pipe_stdout[1], retain=False)
        self.task.schedule(self.worker)
        self.task.resume()

    def send(self, msg):
        """send msg (bytes) to pseudo stdin"""
        os.write(self.pipe_stdin[1], msg + b'\n')

    def send_str(self, msgstr):
        """send msg (string) to pseudo stdin"""
        self.send(msgstr.encode())

    def recv(self):
        """recv buf from pseudo stdout (blocking call with timeout)"""
        if not select.select([self.pipe_stdout[0]], [], [], RECV_TIMEOUT)[0]:
            raise RuntimeError("no gateway reply after %ds" % RECV_TIMEOUT)
        return os.read(self.pipe_stdout[0], 4096)

    def wait(self):
        """wait for task/thread termination"""
        # can be blocked indefinitely if StreamWorker doesn't complete
        self.task.join()

    def close(self):
        """close parent fds"""
        os.close(self.pipe_stdout[0])
        os.close(self.pipe_stdin[1])

    def destroy(self):
        """abort task/thread"""
        self.task.abort(kill=True)


class TreeGatewayBaseTest(unittest.TestCase):
    """base test class"""

    def setUp(self):
        """setup gateway and topology for each test"""
        # gateway
        self.gateway = Gateway()
        self.chan = self.gateway.channel
        # topology
        graph = TopologyGraph()
        graph.add_route(NodeSet(HOSTNAME), NodeSet('n[1-2]'))
        graph.add_route(NodeSet('n1'), NodeSet('n[10-49]'))
        graph.add_route(NodeSet('n2'), NodeSet('n[50-89]'))
        self.topology = graph.to_tree(HOSTNAME)
        # xml parser with Communication.XMLReader as content handler
        self.xml_reader = XMLReader()
        self.parser = xml.sax.make_parser(["IncrementalParser"])
        self.parser.setContentHandler(self.xml_reader)

    def tearDown(self):
        """destroy gateway after each test"""
        self.gateway.destroy()
        self.gateway = None

    #
    # Send to GW
    #
    def channel_send_start(self):
        """send starting channel tag"""
        self.gateway.send_str('<channel version="%s">' % __version__)

    def channel_send_stop(self):
        """send channel ending tag"""
        self.gateway.send_str("</channel>")

    def channel_send_cfg(self, gateway):
        """send configuration part of channel"""
        # code snippet from PropagationChannel.start()
        cfg = ConfigurationMessage(gateway)
        cfg.data_encode(self.topology)
        self.gateway.send(cfg.xml())

    #
    # Receive from GW
    #
    def assert_isinstance(self, msg, msg_class):
        """helper to check a message instance"""
        self.assertTrue(isinstance(msg, msg_class),
                        "%s is not a %s" % (type(msg), msg_class))

    def _recvxml(self):
        while not self.xml_reader.msg_available():
            xml_msg = self.gateway.recv()
            if len(xml_msg) == 0:
                self.parser.close()
                break
            self.assertTrue(type(xml_msg) is bytes)
            self.parser.feed(xml_msg)
            if hasattr(self.parser, 'flush'):  # >=3.13 and backports
                self.parser.flush()

        return self.xml_reader.pop_msg()

    def recvxml(self, expected_msg_class=None):
        msg = self._recvxml()
        if expected_msg_class is None:
            self.assertEqual(msg, None)
        else:
            self.assert_isinstance(msg, expected_msg_class)
        return msg


class TreeGatewayTest(TreeGatewayBaseTest):

    def test_basic_noop(self):
        """test gateway channel open/close"""
        self.channel_send_start()
        self.recvxml(StartMessage)
        self.assertEqual(self.chan.opened, True)
        self.assertEqual(self.chan.setup, False)

        self.channel_send_stop()
        self.recvxml(EndMessage)
        # ending tag should abort gateway worker without delay
        self.gateway.wait()
        self.gateway.close()

    def test_channel_err_dup(self):
        """test gateway channel duplicate tags"""
        self.channel_send_start()
        msg = self.recvxml(StartMessage)
        self.assertEqual(self.chan.opened, True)
        self.assertEqual(self.chan.setup, False)

        # send an unexpected second channel tag
        self.channel_send_start()
        msg = self.recvxml(ErrorMessage)
        self.assertEqual(msg.type, 'ERR')
        reason = 'unexpected message: Message CHA '
        self.assertEqual(msg.reason[:len(reason)], reason)

        # gateway should terminate channel session
        msg = self.recvxml(EndMessage)
        self.gateway.wait()
        self.gateway.close()

    def _check_channel_err(self, sendmsg, errback, openchan=True,
                           setupchan=False):
        """helper to ease test of erroneous messages sent to gateway"""
        if openchan:
            self.channel_send_start()
            msg = self.recvxml(StartMessage)
            self.assertEqual(self.chan.opened, True)
            self.assertEqual(self.chan.setup, False)

        if setupchan:
            # send channel configuration
            self.channel_send_cfg('n1')
            msg = self.recvxml(ACKMessage)
            self.assertEqual(self.chan.setup, True)

        # send the erroneous message and test gateway reply
        self.gateway.send_str(sendmsg)
        msg = self.recvxml(ErrorMessage)
        self.assertEqual(msg.type, 'ERR')
        try:
            if not errback.search(msg.reason):
                self.assertFalse(msg.reason)
        except AttributeError:
            # not a regex
            self.assertEqual(msg.reason, errback)

        # gateway should terminate channel session
        if openchan:
            msg = self.recvxml(EndMessage)
            self.assertEqual(msg.type, 'END')
        else:
            self.recvxml()

        # gateway task should exit properly
        self.gateway.wait()
        self.gateway.close()

    def test_err_start_with_ending_tag(self):
        """test gateway missing opening channel tag"""
        self._check_channel_err('</channel>',
                                'Parse error: not well-formed (invalid token)',
                                openchan=False)

    def test_err_channel_end_msg(self):
        """test gateway channel missing opening message tag"""
        self._check_channel_err('</message>',
                                'Parse error: mismatched tag')

    def test_err_channel_end_msg_setup(self):
        """test gateway channel missing opening message tag (setup)"""
        self._check_channel_err('</message>',
                                'Parse error: mismatched tag',
                                setupchan=True)

    def test_err_unknown_tag(self):
        """test gateway unknown tag"""
        self._check_channel_err('<foobar></footbar>',
                                'Invalid starting tag foobar',
                                openchan=False)

    def test_channel_err_unknown_tag(self):
        """test gateway unknown tag in channel"""
        self._check_channel_err('<foo></foo>', 'Invalid starting tag foo')

    def test_channel_err_unknown_tag_setup(self):
        """test gateway unknown tag in channel (setup)"""
        self._check_channel_err('<foo></foo>',
                                'Invalid starting tag foo',
                                setupchan=True)

    def test_err_unknown_msg(self):
        """test gateway unknown message"""
        self._check_channel_err('<message msgid="24" type="ABC"></message>',
                                'Unknown message type ABC',
                                openchan=False)

    def test_channel_err_unknown_msg(self):
        """test gateway channel unknown message"""
        self._check_channel_err('<message msgid="24" type="ABC"></message>',
                                'Unknown message type ABC')

    def test_channel_err_no_type_msg(self):
        """test gateway channel message with no type"""
        self._check_channel_err('<message msgid="24"></message>',
                                'Unknown message with no type')

    def test_channel_err_empty_type_msg(self):
        """test gateway channel message with empty type"""
        self._check_channel_err('<message msgid="24" type=""></message>',
                                'Unknown message with no type')

    def test_err_xml_malformed(self):
        """test gateway malformed xml message"""
        self._check_channel_err('<message type="ABC"</message>',
                                'Parse error: not well-formed (invalid token)',
                                openchan=False)

    def test_channel_err_xml_malformed(self):
        """test gateway channel malformed xml message"""
        self._check_channel_err('<message type="ABC"</message>',
                                'Parse error: not well-formed (invalid token)')

    def test_channel_err_xml_malformed_setup(self):
        """test gateway channel malformed xml message"""
        self._check_channel_err('<message type="ABC"</message>',
                                'Parse error: not well-formed (invalid token)',
                                setupchan=True)

    def test_channel_err_xml_bad_char(self):
        """test gateway channel malformed xml message (bad chars)"""
        self._check_channel_err('\x11<message type="ABC"></message>',
                                'Parse error: not well-formed (invalid token)')

    def test_channel_err_missingattr(self):
        """test gateway channel message bad attributes"""
        self._check_channel_err(
            '<message msgid="24" nodes="foo" retcode="4" type="RET"></message>',
            'Invalid "message" attributes: missing key "srcid"')

    def test_channel_err_unexpected(self):
        """test gateway channel unexpected message"""
        self._check_channel_err(
            '<message type="ACK" ack="2" msgid="2"></message>',
            re.compile(r'unexpected message: Message ACK \(.*ack: 2.*\)'))

    def test_channel_err_cfg_missing_gw(self):
        """test gateway channel message missing gateway nodename"""
        self._check_channel_err(
            '<message msgid="337" type="CFG">DUMMY</message>',
            'Invalid "message" attributes: missing key "gateway"')

    def test_channel_err_missing_pl(self):
        """test gateway channel message missing payload"""
        self._check_channel_err(
            '<message msgid="14" type="CFG" gateway="n1"></message>',
            re.compile(r'Message CFG has an invalid payload'))

    def test_channel_err_unexpected_pl(self):
        """test gateway channel message unexpected payload"""
        self._check_channel_err(
            '<message msgid="14" type="ERR" reason="test">FOO</message>',
            'Got unexpected payload for Message ERR', setupchan=True)

    def test_channel_err_badenc_b2a_pl(self):
        """test gateway channel message badly encoded payload (base64)"""
        # Generate TypeError (py2) or binascii.Error (py3)
        self._check_channel_err(
            '<message msgid="14" type="CFG" gateway="n1">bar</message>',
            re.compile(r'Message CFG has an invalid payload'))

    def test_channel_err_badenc_pickle_pl(self):
        """test gateway channel message badly encoded payload (pickle)"""
        # Generate pickle error
        self._check_channel_err(
            '<message msgid="14" type="CFG" gateway="n1">barm</message>',
            re.compile(r'Message CFG has an invalid payload'))

    def test_channel_err_pickle_proto_pl(self):
        """test gateway channel message payload with unknown pickle protocol"""
        # Generate ValueError (unsupported pickle protocol: 7)
        payload = base64.b64encode(b'\x80\x07spam').decode()
        self._check_channel_err(
            '<message msgid="14" type="CFG" gateway="n1">%s</message>'
            % payload,
            re.compile(r'Message CFG has an invalid payload'))

    def test_channel_basic_abort(self):
        """test gateway channel aborted while opened"""
        self.channel_send_start()
        self.recvxml(StartMessage)
        self.assertEqual(self.chan.opened, True)
        self.assertEqual(self.chan.setup, False)
        self.gateway.close()
        self.gateway.wait()

    def _check_channel_ctl_shell(self, command, target, stderr, remote,
                                 reply_msg_class, reply_pattern,
                                 write_buf=None, timeout=-1, replycnt=1,
                                 reply_rc=0):
        """helper to check channel shell action"""
        self.channel_send_start()
        msg = self.recvxml(StartMessage)
        self.channel_send_cfg('n1')
        msg = self.recvxml(ACKMessage)

        # prepare a remote shell command request...
        workertree = TreeWorker(nodes=target, handler=None, timeout=timeout,
                                command=command)
        # code snippet from PropagationChannel.shell()
        ctl = ControlMessage(id(workertree))
        ctl.action = 'shell'
        ctl.target = NodeSet(target)

        info = task_self()._info.copy()
        info['debug'] = False

        ctl_data = {
            'cmd': command,
            'invoke_gateway': workertree.invoke_gateway,
            'taskinfo': info,
            'stderr': stderr,
            'timeout': timeout,
            'remote': remote
        }
        ctl.data_encode(ctl_data)
        self.gateway.send(ctl.xml())

        self.recvxml(ACKMessage)

        if write_buf:
            ctl = ControlMessage(id(workertree))
            ctl.action = 'write'
            ctl.target = NodeSet(target)
            ctl_data = {
                'buf': write_buf,
            }
            # Send write message
            ctl.data_encode(ctl_data)
            self.gateway.send(ctl.xml())
            self.recvxml(ACKMessage)

            # Send EOF message
            ctl = ControlMessage(id(workertree))
            ctl.action = 'eof'
            ctl.target = NodeSet(target)
            self.gateway.send(ctl.xml())
            self.recvxml(ACKMessage)

        while replycnt > 0:
            msg = self.recvxml(reply_msg_class)
            replycnt -= len(NodeSet(msg.nodes))
            self.assertTrue(msg.nodes in ctl.target)
            if msg.has_payload or reply_pattern:
                msg_data = msg.data_decode()
                try:
                    if not reply_pattern.search(msg_data):
                        self.assertEqual(msg.data, reply_pattern,
                                         'Pattern "%s" not found in data="%s"'
                                         % (reply_pattern.pattern, msg_data))
                except AttributeError:
                    # not a regexp
                    self.assertEqual(msg_data, reply_pattern)

        if timeout <= 0:
            msg = self.recvxml(RetcodeMessage)
            self.assertEqual(msg.retcode, reply_rc)

        self.channel_send_stop()
        self.gateway.wait()
        self.gateway.close()

    def test_channel_ctl_shell_local1(self):
        """test gateway channel shell stdout (stderr=False remote=False)"""
        self._check_channel_ctl_shell("echo ok", "n10", False, False,
                                      StdOutMessage, b"ok")

    def test_channel_ctl_shell_local2(self):
        """test gateway channel shell stdout (stderr=True remote=False)"""
        self._check_channel_ctl_shell("echo ok", "n10", True, False,
                                      StdOutMessage, b"ok")

    def test_channel_ctl_shell_local3(self):
        """test gateway channel shell stderr (stderr=True remote=False)"""
        self._check_channel_ctl_shell("echo ok >&2", "n10", True, False,
                                      StdErrMessage, b"ok")

    def test_channel_ctl_shell_mlocal1(self):
        """test gateway channel shell multi (remote=False)"""
        self._check_channel_ctl_shell("echo ok", "n[10-49]", True, False,
                                      StdOutMessage, b"ok", replycnt=40)

    def test_channel_ctl_shell_mlocal2(self):
        """test gateway channel shell multi stderr (remote=False)"""
        self._check_channel_ctl_shell("echo ok 1>&2", "n[10-49]", True, False,
                                      StdErrMessage, b"ok", replycnt=40)

    def test_channel_ctl_shell_mlocal3(self):
        """test gateway channel shell multi placeholder (remote=False)"""
        self._check_channel_ctl_shell('echo node %h rank %n', "n[10-29]", True,
                                      False, StdOutMessage,
                                      re.compile(br"node n\d+ rank \d+"),
                                      replycnt=20)

    def test_channel_ctl_shell_remote1(self):
        """test gateway channel shell stdout (stderr=False remote=True)"""
        self._check_channel_ctl_shell("echo ok", "n10", False, True,
                                      StdOutMessage,
                                      re.compile(b"(Could not resolve hostname|"
                                                 b"Name or service not known)"),
                                      reply_rc=255)

    def test_channel_ctl_shell_remote2(self):
        """test gateway channel shell stdout (stderr=True remote=True)"""
        self._check_channel_ctl_shell("echo ok", "n10", True, True,
                                      StdErrMessage,
                                      re.compile(b"(Could not resolve hostname|"
                                                 b"Name or service not known)"),
                                      reply_rc=255)

    def test_channel_ctl_shell_timeo1(self):
        """test gateway channel shell timeout"""
        self._check_channel_ctl_shell("sleep 10", "n10", False, False,
                                      TimeoutMessage, None, timeout=0.5)

    def test_channel_ctl_shell_wrloc1(self):
        """test gateway channel write (stderr=False remote=False)"""
        self._check_channel_ctl_shell("cat", "n10", False, False,
                                      StdOutMessage, b"ok", write_buf=b"ok\n")

    def test_channel_ctl_shell_wrloc2(self):
        """test gateway channel write (stderr=True remote=False)"""
        self._check_channel_ctl_shell("cat", "n10", True, False,
                                      StdOutMessage, b"ok", write_buf=b"ok\n")

    def test_channel_ctl_shell_mwrloc1(self):
        """test gateway channel write multi (remote=False)"""
        self._check_channel_ctl_shell("cat", "n[10-49]", True, False,
                                      StdOutMessage, b"ok", write_buf=b"ok\n")


class TreeMessageTest(unittest.TestCase):
    """test tree communication messages (no gateway needed)"""

    def test_msg_pickle_protocol(self):
        """test message payload pickle protocol pin (wire format)"""
        msg = ConfigurationMessage('n1')
        msg.data_encode({'foo': 'bar'})
        raw = base64.b64decode(msg.data)
        # pickle protocol 2+ starts with PROTO opcode then protocol number
        self.assertEqual(raw[0:1], b'\x80')
        self.assertLessEqual(bytearray(raw)[1], 4)  # bytearray for py2 compat
        self.assertEqual(msg.data_decode(), {'foo': 'bar'})


class ChannelWorkerStub(object):
    """stub channel worker for head-side channel tests"""

    def __init__(self):
        self.aborted = False

    def write(self, buf, sname=None):
        return len(buf)

    def abort(self):
        self.aborted = True


class MetaWorkerStub(object):
    """stub metaworker recording remote node messages"""

    def __init__(self):
        self.msglines = []

    def _on_remote_node_msgline(self, node, msg, sname, gateway):
        self.msglines.append((node, msg, sname, gateway))


class TreeHeadChannelErrorTest(unittest.TestCase):
    """test head-side (initiator) channel errors (no gateway needed)"""

    def setUp(self):
        self.chan = PropagationChannel(task_self(), 'gw1')
        self.chan.worker = ChannelWorkerStub()
        self.mw = MetaWorkerStub()
        self.chan.workers[id(self.mw)] = self.mw
        # gateway greeting opens the channel
        self.chan.ev_read(self.chan.worker, 'gw1', self.chan.SNAME_READER,
                          ('<channel version="%s">' % __version__).encode())
        self.assertTrue(self.chan.opened)

    def test_head_channel_err_invalid_tag(self):
        """test head channel invalid tag reported as stderr"""
        self.chan.ev_read(self.chan.worker, 'gw1', self.chan.SNAME_READER,
                          b'<foo></foo>')
        [(node, msg, sname, gateway)] = self.mw.msglines
        self.assertEqual(node, 'gw1')
        self.assertEqual(msg, b'Invalid starting tag foo')
        self.assertEqual(sname, 'stderr')
        self.assertEqual(gateway, 'gw1')
        # fatal channel error: channel must be closed
        self.assertTrue(self.chan.worker.aborted)
        self.assertFalse(self.chan.opened)

    def test_head_channel_err_parse_error(self):
        """test head channel parse error reported as stderr"""
        self.chan.ev_read(self.chan.worker, 'gw1', self.chan.SNAME_READER,
                          b'<message type="ABC"</message>')
        [(node, msg, sname, gateway)] = self.mw.msglines
        self.assertEqual(node, 'gw1')
        self.assertTrue(isinstance(msg, bytes))
        self.assertIn(b'not well-formed', msg)
        self.assertEqual(sname, 'stderr')
        self.assertEqual(gateway, 'gw1')
        # fatal channel error: channel must be closed
        self.assertTrue(self.chan.worker.aborted)
        self.assertFalse(self.chan.opened)

    def test_head_channel_gw_error_before_setup(self):
        """test gateway error before setup reported as stderr"""
        self.chan.ev_read(self.chan.worker, 'gw1', self.chan.SNAME_READER,
                          b'<message type="ERR" msgid="0" reason="Message CFG '
                          b'has an invalid payload (unsupported pickle '
                          b'protocol: 5)"></message>')
        [(node, msg, sname, gateway)] = self.mw.msglines
        self.assertEqual(node, 'gw1')
        self.assertEqual(msg, b'Message CFG has an invalid payload'
                              b' (unsupported pickle protocol: 5)')
        self.assertEqual(sname, 'stderr')
        self.assertEqual(gateway, 'gw1')

    def test_head_channel_gw_error_empty_reason(self):
        """test gateway error with empty reason reported as empty line"""
        self.chan.ev_read(self.chan.worker, 'gw1', self.chan.SNAME_READER,
                          b'<message type="ERR" msgid="0" reason=""></message>')
        self.assertEqual(self.mw.msglines, [('gw1', b'', 'stderr', 'gw1')])

    def test_head_channel_gw_error_after_setup(self):
        """test gateway error after setup raises TopologyError"""
        # gateway ACK completes channel setup
        self.chan.ev_read(self.chan.worker, 'gw1', self.chan.SNAME_READER,
                          b'<message type="ACK" msgid="0" ack="0"></message>')
        self.assertTrue(self.chan.setup)
        self.assertRaises(TopologyError, self.chan.ev_read, self.chan.worker,
                          'gw1', self.chan.SNAME_READER,
                          b'<message type="ERR" msgid="1" reason="bad news">'
                          b'</message>')
        self.assertEqual(self.mw.msglines, [])
