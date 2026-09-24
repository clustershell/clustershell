"""ASV benchmarks for ClusterShell.RangeSet"""

from ClusterShell.RangeSet import RangeSet

# module-level state: a setup() hook would disable timeit batching (asv_runner 0.3.x)
SINGLES = ",".join(str(i) for i in range(0, 40000, 2))
RNGLIST = ["%d-%d" % (i, i + 5) for i in range(0, 100000, 10)]
INTS = list(range(20000))

DENSE = RangeSet("0-99999")
SPARSE = RangeSet("0-199998/2")
PADDED = RangeSet("000000-099999")
STEPPED = RangeSet("0-299999/3", autostep=3)
SMALL = RangeSet("0-9999")
RS_B = RangeSet("50000-149999")
RS_SMALL = RangeSet("0-99")

# pre-warm sorted views so fold benchmarks measure steady state
for _rset in (DENSE, SPARSE, PADDED, STEPPED, SMALL):
    str(_rset)


class RangeSetParse:
    """Build RangeSet objects from patterns."""

    def time_parse_dense(self):
        RangeSet("0-99999")

    def time_parse_stepped(self):
        RangeSet("0-299999/3")

    def time_parse_singles(self):
        RangeSet(SINGLES)

    def time_from_ints(self):
        RangeSet(INTS)

    def time_fromlist(self):
        RangeSet.fromlist(RNGLIST)

    def time_parse_and_fold(self):
        str(RangeSet("0-99999"))


class RangeSetFold:
    """Fold prebuilt RangeSet objects back to strings (steady state)."""

    def time_str_dense(self):
        str(DENSE)

    def time_str_sparse(self):
        str(SPARSE)

    def time_str_padded(self):
        str(PADDED)

    def time_str_autostep(self):
        str(STEPPED)


class RangeSetAccess:
    """Iteration, indexing and lookup on a prebuilt RangeSet."""

    def time_iterate(self):
        list(DENSE)

    def time_index(self):
        DENSE[50000]

    def time_slice(self):
        DENSE[10:99990:7]

    def time_padding(self):
        DENSE.padding

    def time_contains_str(self):
        "54321" in DENSE

    def time_contains_int(self):
        54321 in DENSE

    def time_split(self):
        for chunk in SMALL.split(32):
            pass

    def time_copy(self):
        DENSE.copy()


class RangeSetOps:
    """Set arithmetic between prebuilt RangeSet objects."""

    def time_union(self):
        DENSE.union(RS_B)

    def time_intersection_small(self):
        DENSE.intersection(RS_SMALL)

    def time_difference(self):
        DENSE.difference(RS_B)

    def time_symmetric_difference(self):
        DENSE.symmetric_difference(RS_B)
