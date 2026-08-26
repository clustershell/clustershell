"""ASV benchmarks for ClusterShell.NodeSet"""

from ClusterShell.NodeSet import NodeSet

PLAIN = ["node%d" % i for i in range(20000)]
PREFIXED = ["p%02dn%d" % (i % 50, i) for i in range(20000)]

NS = NodeSet("node[0-99999]")
NS_SMALL = NodeSet("node[0-9999]")
NS_B = NodeSet("node[50000-149999]")
ND_A = NodeSet("r[0-19]c[0-39]n[0-9]")
ND_B = NodeSet("r[10-29]c[20-59]n[0-9]")

for _nset in (NS, NS_SMALL):
    str(_nset)


class NodeSetParse:
    """Build NodeSet objects from patterns and node lists."""

    def time_parse_bracket(self):
        NodeSet("node[0-99999]")

    def time_parse_and_fold(self):
        str(NodeSet("node[0-99999]"))

    def time_fromlist_plain(self):
        NodeSet.fromlist(PLAIN)

    def time_fromlist_prefixes(self):
        NodeSet.fromlist(PREFIXED)

    def time_parse_nd(self):
        NodeSet("r[0-19]c[0-39]n[0-9]")

    def time_parse_and_fold_nd(self):
        str(NodeSet("r[0-19]c[0-39]n[0-9]"))


class NodeSetAccess:
    """Iteration, indexing and lookup on a prebuilt NodeSet."""

    def time_str(self):
        str(NS)

    def time_iterate(self):
        list(NS)

    def time_index(self):
        NS[50000]

    def time_contains(self):
        "node54321" in NS

    def time_split(self):
        for chunk in NS_SMALL.split(32):
            pass


class NodeSetOps:
    """Set arithmetic between prebuilt NodeSet objects."""

    def time_union(self):
        NS | NS_B

    def time_difference(self):
        NS.difference(NS_B)

    def time_union_nd(self):
        ND_A | ND_B

    def time_difference_nd(self):
        ND_A.difference(ND_B)

    def time_union_and_fold_nd(self):
        str(ND_A | ND_B)
