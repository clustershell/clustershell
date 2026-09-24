"""ASV benchmarks for ClusterShell import time (CLI startup cost)"""


class Imports:
    """Cold import cost of the main library entry points."""

    def timeraw_import_nodeset(self):
        return "import ClusterShell.NodeSet"

    def timeraw_import_task(self):
        return "import ClusterShell.Task"
