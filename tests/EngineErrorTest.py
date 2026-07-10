"""
Unit test for Engine event loop error handling
"""

import errno
import select
import unittest

import ClusterShell.Engine.Select
from ClusterShell.Engine.Engine import EngineNotSupportedError
from ClusterShell.Engine.EPoll import EngineEPoll
from ClusterShell.Engine.Select import EngineSelect


class EngineErrorTest(unittest.TestCase):
    """test that non-EINTR event loop errors propagate"""

    def test_epoll_error(self):
        """test EPoll engine non-EINTR error propagation"""
        try:
            engine = EngineEPoll({})
        except EngineNotSupportedError:
            self.skipTest("engine epoll not supported on this host")

        class BadPoller(object):
            def poll(self, *args):
                raise IOError(errno.EBADF, "injected error")

        engine.epolling.close()
        engine.epolling = BadPoller()
        engine.evlooprefcnt = 1
        self.assertRaises(IOError, engine.runloop, None)

    def test_select_error(self):
        """test Select engine non-EINTR error propagation"""
        engine = EngineSelect({})

        class BadSelect(object):
            error = select.error

            @staticmethod
            def select(*args):
                raise select.error(errno.EINVAL, "injected error")

        select_mod = ClusterShell.Engine.Select.select
        ClusterShell.Engine.Select.select = BadSelect
        try:
            engine.evlooprefcnt = 1
            self.assertRaises(select.error, engine.runloop, None)
        finally:
            ClusterShell.Engine.Select.select = select_mod
