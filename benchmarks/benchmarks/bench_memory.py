"""ASV benchmarks for ClusterShell peak memory usage"""

from ClusterShell.NodeSet import NodeSet
from ClusterShell.RangeSet import RangeSet

# no module-level objects here: they would inflate the process RSS baseline


class Memory:
    """Peak memory while building large objects."""

    def peakmem_rangeset_1m(self):
        RangeSet("0-999999")

    def peakmem_nodeset_1m(self):
        NodeSet("node[0-999999]")
