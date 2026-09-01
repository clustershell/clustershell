# ClusterShell (local) test suite -- python -O test lane
# Written by S. Thiell

"""Unit test for ClusterShell Engine with assert statements stripped

Tests in *Test_O.py files validate the library running under python -O,
where its internal assert statements are stripped. They are kept out of
the regular *Test.py discovery pattern; run them from the source tree
root with:

    $ python -O -m unittest discover -v -s tests -p '*Test_O.py' -t .

Never use bare assert statements in these files: python -O strips them,
silently turning tests into no-ops (enforced by OptimizedLaneTest).
"""

import ast
import glob
import os
import unittest

from ClusterShell.Task import task_self
from ClusterShell.Event import EventHandler
from ClusterShell.Worker.Worker import StreamWorker


@unittest.skipIf(__debug__, "requires python -O")
class EngineTestO(unittest.TestCase):

    def test_abort_on_ev_start(self):
        """test pending client accounting on abort from ev_start"""
        class Aborter(EventHandler):
            def ev_start(self, worker):
                worker.abort()

        class Spawner(EventHandler):
            def ev_timer(self, timer):
                # in-fly add: register(client._start()) runs outside any scan
                task_self().schedule(StreamWorker(handler=Aborter()))

        task = task_self()
        engine = task._engine
        self.assertEqual(engine._reg_stats.get('default', 0), 0)
        task.timer(0.1, handler=Spawner())
        try:
            task.resume()
        finally:
            # drop ghost fanout slot: register() completed on removed client
            engine._reg_stats.pop('default', None)
        self.assertEqual(engine._nunreg, 0)


class OptimizedLaneTest(unittest.TestCase):

    def test_no_bare_assert(self):
        """test that lane files do not use bare assert statements"""
        testdir = os.path.dirname(os.path.abspath(__file__))
        for path in glob.glob(os.path.join(testdir, '*Test_O.py')):
            with open(path) as srcfile:
                tree = ast.parse(srcfile.read(), path)
            lines = [str(node.lineno) for node in ast.walk(tree)
                     if isinstance(node, ast.Assert)]
            self.assertEqual([], lines,
                             "bare assert (no-op under -O) in %s at line(s) "
                             "%s" % (os.path.basename(path), ', '.join(lines)))
