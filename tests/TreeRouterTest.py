# ClusterShell propagation tree router test suite

"""Unit test for ClusterShell PropagationTreeRouter"""

import unittest
from tempfile import NamedTemporaryFile

from ClusterShell.NodeSet import NodeSet
from ClusterShell.Propagation import PropagationTreeRouter, RouteResolvingError
from ClusterShell.Topology import TopologyParser


class TreeRouterTest(unittest.TestCase):
    """test PropagationTreeRouter gateway selection and route weights"""

    def _tree(self, topoconf, root='admin'):
        """helper to build a topology tree from a config string"""
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(topoconf)
            tmpfile.flush()
            parser = TopologyParser(tmpfile.name)
            return parser.tree(root)

    def _router(self, topoconf, root='admin'):
        """helper to build a PropagationTreeRouter from a config string"""
        return PropagationTreeRouter(root, self._tree(topoconf, root))

    def _distribution(self, router, targets):
        """helper to get the target distribution per gateway"""
        dist = {}
        for gateway, dstset in router.dispatch(NodeSet(targets)):
            dist.setdefault(str(gateway), NodeSet()).add(dstset)
        return dist

    def testDispatchBalanced(self):
        """test dispatch without weights (balanced)"""
        router = self._router(b'[routes]\n'
                              b'admin: gw[1-2]\n'
                              b'gw[1-2]: nodes[0-11]\n')
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw1', 'gw2'])
        self.assertEqual(len(dist['gw1']), 6)
        self.assertEqual(len(dist['gw2']), 6)

    def testDispatchWeighted(self):
        """test dispatch with weights"""
        router = self._router(b'[routes]\n'
                              b'admin: gw[1-2]\n'
                              b'gw[1-2]: nodes[0-11]\n'
                              b'[weights]\n'
                              b'gw1: 2\n')
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw1', 'gw2'])
        self.assertEqual(len(dist['gw1']), 8)
        self.assertEqual(len(dist['gw2']), 4)

    def testDispatchStandby(self):
        """test dispatch with zero-weight standby gateway"""
        router = self._router(b'[routes]\n'
                              b'admin: gw[1-2],gwb\n'
                              b'gw[1-2],gwb: nodes[0-11]\n'
                              b'[weights]\n'
                              b'gwb: 0\n')
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw1', 'gw2'])
        self.assertEqual(len(dist['gw1']), 6)
        self.assertEqual(len(dist['gw2']), 6)

    def testDispatchStandbyFailover(self):
        """test dispatch failover to standby gateway"""
        router = self._router(b'[routes]\n'
                              b'admin: gw[1-2],gwb\n'
                              b'gw[1-2],gwb: nodes[0-11]\n'
                              b'[weights]\n'
                              b'gwb: 0\n')
        router.mark_unreachable('gw1')
        router.mark_unreachable('gw2')
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gwb'])
        self.assertEqual(len(dist['gwb']), 12)

    def testDispatchAllStandby(self):
        """test dispatch with only zero-weight gateways (balanced)"""
        router = self._router(b'[routes]\n'
                              b'admin: gw[1-2]\n'
                              b'gw[1-2]: nodes[0-11]\n'
                              b'[weights]\n'
                              b'gw[1-2]: 0\n')
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw1', 'gw2'])
        self.assertEqual(len(dist['gw1']), 6)
        self.assertEqual(len(dist['gw2']), 6)

    def testDispatchWeightsDeeperLevel(self):
        """test route weights used from a gateway node"""
        tree = self._tree(b'[routes]\n'
                          b'admin: gwa[1-2]\n'
                          b'gwa[1-2]: gwb[1-2]\n'
                          b'gwb[1-2]: nodes[0-11]\n'
                          b'[weights]\n'
                          b'gwb1: 2\n')
        # a gateway builds its own router from the propagated tree
        router = PropagationTreeRouter('gwa1', tree)
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gwb1', 'gwb2'])
        self.assertEqual(len(dist['gwb1']), 8)
        self.assertEqual(len(dist['gwb2']), 4)

    def testAllUnreachable(self):
        """test resolution error with all gateways unreachable"""
        router = self._router(b'[routes]\n'
                              b'admin: gw[1-2],gwb\n'
                              b'gw[1-2],gwb: nodes[0-11]\n'
                              b'[weights]\n'
                              b'gwb: 0\n')
        router.mark_unreachable('gw1')
        router.mark_unreachable('gw2')
        router.mark_unreachable('gwb')
        self.assertRaises(RouteResolvingError, router.next_hop,
                          NodeSet('nodes5'))
        self.assertRaises(RouteResolvingError, list,
                          router.dispatch(NodeSet('nodes[0-11]')))

    def testTopologyWithoutWeightsAttr(self):
        """test router with a topology tree lacking weights (pre-1.11)"""
        tree = self._tree(b'[routes]\n'
                          b'admin: gw[1-2]\n'
                          b'gw[1-2]: nodes[0-11]\n')
        # simulate a tree unpickled from an older ClusterShell version
        del tree.weights
        router = PropagationTreeRouter('admin', tree)
        self.assertEqual(router.weights, {})
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(len(dist['gw1']), 6)
        self.assertEqual(len(dist['gw2']), 6)


if __name__ == '__main__':
    unittest.main()
