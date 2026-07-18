# ClusterShell propagation tree router test suite

"""Unit test for ClusterShell PropagationTreeRouter"""

import pickle
import unittest
from textwrap import dedent

from ClusterShell.Communication import GW_PICKLE_PROTOCOL
from ClusterShell.NodeSet import NodeSet
from ClusterShell.Propagation import PropagationTreeRouter, RouteResolvingError
from ClusterShell.Topology import TopologyParser
from .TLib import make_temp_file


class TreeRouterTest(unittest.TestCase):
    """test PropagationTreeRouter gateway selection and priorities"""

    def _tree(self, topoconf, suffix='.yaml', root='admin'):
        """helper to build a topology tree from a config string"""
        tmpfile = make_temp_file(dedent(topoconf).encode(), suffix=suffix)
        try:
            return TopologyParser(tmpfile.name).tree(root)
        finally:
            tmpfile.close()

    def _router(self, topoconf, suffix='.yaml', root='admin'):
        """helper to build a PropagationTreeRouter from a config string"""
        return PropagationTreeRouter(root, self._tree(topoconf, suffix, root))

    def _distribution(self, router, targets):
        """helper to get the target distribution per gateway"""
        dist = {}
        for gateway, dstset in router.dispatch(NodeSet(targets)):
            dist.setdefault(str(gateway), NodeSet()).add(dstset)
        return dist

    def testDispatchBalancedIni(self):
        """test dispatch with INI gateway pool (balanced)"""
        router = self._router("""
            [routes]
            admin: gw[1-2]
            gw[1-2]: nodes[0-11]
            """, suffix='.conf')
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw1', 'gw2'])
        self.assertEqual(len(dist['gw1']), 6)
        self.assertEqual(len(dist['gw2']), 6)

    def testDispatchBalancedYaml(self):
        """test dispatch with YAML gateway pool (balanced)"""
        router = self._router("""
            routes:
              - gateways: admin
                targets: gw[1-2]
              - gateways: gw[1-2]
                targets: nodes[0-11]
            """)
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw1', 'gw2'])
        self.assertEqual(len(dist['gw1']), 6)
        self.assertEqual(len(dist['gw2']), 6)

    def testDispatchListPool(self):
        """test dispatch with a plain gateway list (load-shared pool)"""
        router = self._router("""
            routes:
              - gateways: admin
                targets: gw[1-2]
              - gateways: [gw1, gw2]
                targets: nodes[0-11]
            """)
        # same priority and weights: same behavior as gateways: gw[1-2]
        self.assertEqual(router.priority_routes, [])
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw1', 'gw2'])
        self.assertEqual(len(dist['gw1']), 6)
        self.assertEqual(len(dist['gw2']), 6)

    def testDispatchPriorityOrder(self):
        """test dispatch with priorities (all to best priority)"""
        router = self._router("""
            routes:
              - gateways: admin
                targets: gw[1-2]
              - gateways:
                  - nodes: gw1
                  - nodes: gw2
                    priority: 2
                targets: nodes[0-11]
            """)
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw1'])
        self.assertEqual(len(dist['gw1']), 12)

    def testDispatchPriorityFailover(self):
        """test dispatch failover to the next priority"""
        router = self._router("""
            routes:
              - gateways: admin
                targets: gw[1-2]
              - gateways:
                  - nodes: gw1
                  - nodes: gw2
                    priority: 2
                targets: nodes[0-11]
            """)
        router.mark_unreachable('gw1')
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw2'])
        self.assertEqual(len(dist['gw2']), 12)

    def testDispatchMutualFailover(self):
        """test dispatch with mutual failover routes"""
        conf = """
            routes:
              - gateways: admin
                targets: gw[1-2]
              - gateways:
                  - nodes: gw1
                  - nodes: gw2
                    priority: 2
                targets: rio[100-109]
              - gateways:
                  - nodes: gw2
                  - nodes: gw1
                    priority: 2
                targets: rio[200-209]
            """
        router = self._router(conf)
        dist = self._distribution(router, 'rio[100-109,200-209]')
        self.assertEqual(sorted(dist), ['gw1', 'gw2'])
        self.assertEqual(str(dist['gw1']), 'rio[100-109]')
        self.assertEqual(str(dist['gw2']), 'rio[200-209]')

        # gw2 keeps its own group and takes over the other one
        router = self._router(conf)
        router.mark_unreachable('gw1')
        dist = self._distribution(router, 'rio[100-109,200-209]')
        self.assertEqual(sorted(dist), ['gw2'])
        self.assertEqual(len(dist['gw2']), 20)

    def testDispatchPriorityBalancedPrimary(self):
        """test dispatch with a balanced primary priority and a spare"""
        conf = """
            routes:
              - gateways: admin
                targets: gw[1-3]
              - gateways:
                  - nodes: gw[1-2]
                  - nodes: gw3
                    priority: 2
                targets: nodes[0-11]
            """
        router = self._router(conf)
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw1', 'gw2'])
        self.assertEqual(len(dist['gw1']), 6)
        self.assertEqual(len(dist['gw2']), 6)

        # spare used when all higher-priority gateways are unreachable
        router = self._router(conf)
        router.mark_unreachable('gw1')
        router.mark_unreachable('gw2')
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw3'])
        self.assertEqual(len(dist['gw3']), 12)

    def testDispatchWeightedPriority(self):
        """test dispatch with weights within a priority"""
        router = self._router("""
            routes:
              - gateways: admin
                targets: gw[1-2]
              - gateways:
                  - nodes: gw1
                    weight: 3
                  - nodes: gw2
                targets: nodes[0-11]
            """)
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw1', 'gw2'])
        self.assertEqual(len(dist['gw1']), 9)
        self.assertEqual(len(dist['gw2']), 3)

    def testDispatchWeightedPriorityNodeSet(self):
        """test dispatch with weights and node sets within a priority"""
        router = self._router("""
            routes:
              - gateways: admin
                targets: gw[1-4]
              - gateways:
                  - nodes: gw[1-2]
                    weight: 2
                  - nodes: gw3
                  - nodes: gw4
                    priority: 2
                targets: nodes[0-9]
            """)
        dist = self._distribution(router, 'nodes[0-9]')
        self.assertEqual(sorted(dist), ['gw1', 'gw2', 'gw3'])
        self.assertEqual(len(dist['gw1']), 4)
        self.assertEqual(len(dist['gw2']), 4)
        self.assertEqual(len(dist['gw3']), 2)

    def testDispatchPrioritiesDeeperLevel(self):
        """test gateway priorities used from a gateway node"""
        conf = """
            routes:
              - gateways: admin
                targets: gwa[1-2]
              - gateways: gwa[1-2]
                targets: gwb[1-2]
              - gateways:
                  - nodes: gwb1
                  - nodes: gwb2
                    priority: 2
                targets: nodes[0-11]
            """
        # admin balances nodes over gwa[1-2] (no priorities at this level)
        router = self._router(conf)
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gwa1', 'gwa2'])

        # a gateway builds its own router from the propagated tree
        router = PropagationTreeRouter('gwa1', self._tree(conf))
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gwb1'])
        self.assertEqual(len(dist['gwb1']), 12)

        router = PropagationTreeRouter('gwa1', self._tree(conf))
        router.mark_unreachable('gwb1')
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gwb2'])

    def testDispatchPrioritySubtree(self):
        """test priorities apply to the subtree below route targets"""
        router = self._router("""
            routes:
              - gateways: admin
                targets: gwa[1-2]
              - gateways:
                  - nodes: gwa1
                  - nodes: gwa2
                    priority: 2
                targets: gwb[1-2]
              - gateways: gwb[1-2]
                targets: nodes[0-11]
            """)
        # nodes are below gwb[1-2]: priorities of the gwa route still apply
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gwa1'])
        self.assertEqual(len(dist['gwa1']), 12)

    def testAllPrioritiesUnreachable(self):
        """test resolution error with all priorities unreachable"""
        router = self._router("""
            routes:
              - gateways: admin
                targets: gw[1-2]
              - gateways:
                  - nodes: gw1
                  - nodes: gw2
                    priority: 2
                targets: nodes[0-11]
            """)
        router.mark_unreachable('gw1')
        router.mark_unreachable('gw2')
        self.assertRaises(RouteResolvingError, router.next_hop,
                          NodeSet('nodes5'))
        self.assertRaises(RouteResolvingError, list,
                          router.dispatch(NodeSet('nodes[0-11]')))

    def testPriorityTreePickle(self):
        """test gateway priorities ride the pickled topology tree"""
        tree = self._tree("""
            routes:
              - gateways: admin
                targets: gw[1-2]
              - gateways:
                  - nodes: gw1
                  - nodes: gw2
                    priority: 2
                targets: nodes[0-11]
            """)
        tree = pickle.loads(pickle.dumps(tree, GW_PICKLE_PROTOCOL))
        router = PropagationTreeRouter('admin', tree)
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(sorted(dist), ['gw1'])

    def testTopologyWithoutPrioritiesAttr(self):
        """test router with a topology tree lacking priorities (pre-1.11)"""
        tree = self._tree("""
            [routes]
            admin: gw[1-2]
            gw[1-2]: nodes[0-11]
            """, suffix='.conf')
        # simulate a tree unpickled from an older ClusterShell version
        del tree.priority_routes
        router = PropagationTreeRouter('admin', tree)
        self.assertEqual(router.priority_routes, [])
        dist = self._distribution(router, 'nodes[0-11]')
        self.assertEqual(len(dist['gw1']), 6)
        self.assertEqual(len(dist['gw2']), 6)


if __name__ == '__main__':
    unittest.main()
