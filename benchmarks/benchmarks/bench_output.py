"""Output processing benchmarks: command output through the event pipeline."""

from ClusterShell.Event import EventHandler
from ClusterShell.Task import task_self
from ClusterShell.Worker.Exec import ExecWorker

# same Task settings as clush: exec worker, separate stderr
TASK = task_self()
TASK.set_default("distant_worker", ExecWorker)
TASK.set_default("stderr", True)
TASK.set_default("stderr_msgtree", False)
TASK.set_info("fanout", 64)


def lines_command(count):
    """Command printing count 64-byte lines."""
    return "awk 'BEGIN { for (i = 0; i < %d; i++) print \"%s\" }'" % (
        count, "x" * 63)


LINES_100K = lines_command(100000)
LINES_10K = lines_command(10000)


class LineHandler(EventHandler):
    """Consume each line, like the clush direct output handler."""

    def __init__(self):
        EventHandler.__init__(self)
        self.lines = 0

    def ev_read(self, worker, node, sname, msg):
        self.lines += 1


class Output:
    """Line delivery from local processes to the caller."""

    def time_ev_read(self):
        # clush default: one ev_read per line, no message tree
        TASK.set_default("stdout_msgtree", False)
        TASK.shell(LINES_100K, nodes="n1", handler=LineHandler(), tree=False,
                   stdin=False)
        TASK.run()

    def time_gather(self):
        # clush -b: 10 processes x 10k lines into the message tree, gathered
        TASK.set_default("stdout_msgtree", True)
        TASK.shell(LINES_10K, nodes="n[1-10]", tree=False, stdin=False)
        TASK.run()
        for msg, nodes in TASK.iter_buffers():
            msg.message()
        TASK.flush_buffers()
