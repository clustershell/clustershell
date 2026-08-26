"""ASV benchmarks for ClusterShell.MsgTree"""

from ClusterShell.MsgTree import MsgTree

NKEYS = 128
NLINES = 100

KEYS = ["node%03d" % i for i in range(NKEYS)]
SHARED_LINES = [b"common output line %d" % i for i in range(NLINES)]
UNIQUE_LINES = [[b"output %d from key %d" % (j, i) for j in range(NLINES)]
                for i in range(NKEYS)]

TREE = MsgTree()
for _key in KEYS:
    for _line in SHARED_LINES:
        TREE.add(_key, _line)

# settle deferred key updates so walk measures steady state
for _msg, _keys in TREE.walk():
    pass


class MsgTreeSuite:
    """Message aggregation as done by clubak and clush -b."""

    def time_add_shared(self):
        tree = MsgTree()
        for key in KEYS:
            for line in SHARED_LINES:
                tree.add(key, line)

    def time_add_unique(self):
        tree = MsgTree()
        for key, lines in zip(KEYS, UNIQUE_LINES):
            for line in lines:
                tree.add(key, line)

    def time_walk(self):
        for msg, keys in TREE.walk():
            pass
