"""Engine benchmarks: local processes driven like clush -R exec."""

from ClusterShell.Task import task_self
from ClusterShell.Worker.Exec import ExecWorker

# same Task settings as clush: exec worker, separate stderr, no message tree
TASK = task_self()
TASK.set_default("distant_worker", ExecWorker)
TASK.set_default("stderr", True)
TASK.set_default("stdout_msgtree", False)
TASK.set_default("stderr_msgtree", False)
TASK.set_info("fanout", 64)

# 4 MiB of stdin in 64 KiB chunks, the read size of the clush stdin thread
STDIN_CHUNKS = [b"x" * 65535 + b"\n"] * 64


class Engine:
    """Process spawning and stdin broadcast through the engine."""

    def time_spawn(self):
        # 1000 trivial commands, 64 at a time (default fanout)
        TASK.shell("true", nodes="n[1-1000]", tree=False, stdin=False)
        TASK.run()

    def time_stdin_broadcast(self):
        # clush < file: every chunk is written to all 8 processes
        worker = TASK.shell("cat > /dev/null", nodes="n[1-8]", tree=False,
                            stdin=True)
        for chunk in STDIN_CHUNKS:
            worker.write(chunk)
        worker.set_write_eof()
        TASK.run()
