"""
Unit test for ClusterShell.Task in tree mode
"""

import logging
import os
from textwrap import dedent
import unittest

from ClusterShell.Propagation import RouteResolvingError
from ClusterShell.Task import Task, task_self
from ClusterShell.Topology import TopologyError

from .TLib import HOSTNAME, make_temp_file

# enable live DEBUG logging when running the tests
logging.basicConfig(level=logging.DEBUG)


class TreeTaskTest(unittest.TestCase):
    """Test cases for Tree-related Task methods"""

    def tearDown(self):
        """clear task topology"""
        task_self().topology = None

    def test_shell_auto_tree_dummy(self):
        """test task shell auto tree"""
        # initialize a dummy topology.conf file
        topofile = make_temp_file(dedent("""
                        [routes]
                        %s: dummy-gw
                        dummy-gw: dummy-node"""% HOSTNAME).encode())
        task = task_self()
        task.set_default("auto_tree", True)
        task.TOPOLOGY_CONFIGS = [topofile.name]

        self.assertRaises(RouteResolvingError, task.run, "/bin/hostname",
                          nodes="dummy-node", stderr=True)
        self.assertEqual(task.max_retcode(), None)

    def test_shell_auto_tree_noconf(self):
        """test task shell auto tree [no topology.conf]"""
        task = task_self()
        task.set_default("auto_tree", True)
        dummyfile = "/some/dummy/path/topo.conf"
        self.assertFalse(os.path.exists(dummyfile))
        task.TOPOLOGY_CONFIGS = [dummyfile]
        # do not raise exception
        task.run("/bin/hostname", nodes="dummy-node")

    def test_shell_auto_tree_error(self):
        """test task shell auto tree [TopologyError]"""
        # initialize an erroneous topology.conf file
        topofile = make_temp_file(dedent("""
                        [routes]
                        %s: dummy-gw
                        dummy-gw: dummy-gw"""% HOSTNAME).encode())
        task = task_self()
        task.set_default("auto_tree", True)
        task.TOPOLOGY_CONFIGS = [topofile.name]
        self.assertRaises(TopologyError, task.run, "/bin/hostname",
                          nodes="dummy-node")

    def test_topology_configs_defaults(self):
        """test default TOPOLOGY_CONFIGS with YAML precedence"""
        # scanned in reverse order: topology.yaml preferred at each location
        scan = Task.TOPOLOGY_CONFIGS[::-1]
        self.assertEqual(len(scan) % 2, 0)
        for conf_path, yaml_path in zip(scan[1::2], scan[0::2]):
            self.assertTrue(yaml_path.endswith('topology.yaml'))
            self.assertTrue(conf_path.endswith('topology.conf'))
            self.assertEqual(os.path.dirname(yaml_path),
                             os.path.dirname(conf_path))

    def test_auto_tree_yaml_precedence(self):
        """test auto tree prefers topology.yaml over topology.conf"""
        conffile = make_temp_file(dedent("""
                        [routes]
                        %s: ini-gw
                        ini-gw: ini-node""" % HOSTNAME).encode())
        yamlfile = make_temp_file(dedent("""
                        routes:
                          - gateways: %s
                            targets: yaml-gw
                          - gateways: yaml-gw
                            targets: yaml-node""" % HOSTNAME).encode(),
                                  suffix='.yaml')
        task = task_self()
        task.set_default("auto_tree", True)
        # mimic default TOPOLOGY_CONFIGS order: YAML after INI at a location
        task.TOPOLOGY_CONFIGS = [conffile.name, yamlfile.name]
        self.assertTrue(task._default_tree_is_enabled())
        self.assertTrue('yaml-gw' in str(task.topology))
