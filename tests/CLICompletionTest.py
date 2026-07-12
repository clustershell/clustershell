# ClusterShell bash-completion test suite
# Written by S. Thiell

"""Unit test for the bash_completion.d/ scripts (clush, cluset).

The functional tests drive the real completion functions (_clush, _cluset)
inside a child bash that sources the system bash-completion library, then
assert on the resulting COMPREPLY array.  They skip gracefully when bash, the
bash-completion library, or clush/cluset (the scripts shell out to them) are
unavailable.  A separate class runs a 'bash -n' syntax check that needs only
bash.
"""

import os
import shutil
import tempfile
import unittest

from subprocess import run, PIPE

# Anchor on this file: tests run via 'unittest discover -t .' from the repo
# root, but CWD must not be assumed.
_TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_TESTS_DIR)
_COMPL_DIR = os.path.join(_REPO_ROOT, "bash_completion.d")

# The completion scripts under test.
_SCRIPTS = ("clush", "cluset")

# Locate the bash-completion runtime library (skip functional tests if absent).
_BC_LIB = next((p for p in ("/usr/share/bash-completion/bash_completion",
                            "/etc/bash_completion",
                            "/usr/local/share/bash-completion/bash_completion")
                if os.access(p, os.R_OK)), None)

# Driver: source the bash-completion library and the completion script under
# test, populate the COMP_* variables, run the completion function and print
# COMPREPLY one entry per line.
_DRIVER = r'''
BC_LIB="$1"; SCRIPT="$2"; FUNC="$3"; shift 3
# /dev/null is the documented way to skip the user's ~/.bash_completion
BASH_COMPLETION_USER_FILE=/dev/null
. "$BC_LIB"
. "$SCRIPT"
COMP_WORDS=("$@")
COMP_CWORD=$(( ${#COMP_WORDS[@]} - 1 ))
COMP_LINE="${COMP_WORDS[*]}"
COMP_POINT=${#COMP_LINE}
COMPREPLY=()
# compopt warns when run outside readline; that diagnostic is harmless here.
"$FUNC" 2>/dev/null || true
((${#COMPREPLY[@]})) && printf '%s\n' "${COMPREPLY[@]}" || true
'''

# Stub cluset printing fixed nodes/groups; shadows the real one via PATH.
_CLUSET_STUB = r'''#!/bin/bash
case "$1" in
--completion)
    printf '%s\n' @stubsrc: @gpu
    if [ $# -gt 1 ]; then printf '%s\n' stubnode1 stubnode2; fi
    ;;
esac
'''


@unittest.skipUnless(shutil.which("bash"), "bash not found")
@unittest.skipUnless(_BC_LIB, "bash-completion library not installed")
@unittest.skipUnless(shutil.which("clush") and shutil.which("cluset"),
                     "clush/cluset not on PATH")
class CLICompletionTest(unittest.TestCase):
    """Drive the bash completion functions in a child bash; check COMPREPLY."""

    def _complete(self, script, func, *words, pathdir=None):
        """Return the completion candidates for the given words; the last word
        is the current word being completed (use '' for an empty word)."""
        path = os.path.join(_COMPL_DIR, script)
        self.assertTrue(os.path.isfile(path), path)
        env = None
        if pathdir:
            env = dict(os.environ, PATH=pathdir + ":" + os.environ["PATH"])
        proc = run(["bash", "-c", _DRIVER, "bash", _BC_LIB, path, func, *words],
                   stdout=PIPE, stderr=PIPE, timeout=30, env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr.decode())
        return proc.stdout.decode().split("\n")[:-1]  # drop trailing empty element

    def _stub_cluset(self):
        """Install the cluset stub in a temp dir; return it for pathdir."""
        tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmpdir)
        stub = os.path.join(tmpdir, "cluset")
        with open(stub, "w") as f:
            f.write(_CLUSET_STUB)
        os.chmod(stub, 0o755)
        return tmpdir

    def test_clush_dash_lists_options(self):
        """clush: bare '-' completes to the option list"""
        reply = self._complete("clush", "_clush", "clush", "-")
        self.assertTrue(len(reply) > 1, reply)
        self.assertIn("--diff ", reply)

    def test_clush_noarg_flag_does_not_swallow_next_word(self):
        """clush: a no-arg flag must not consume the following word (#619)"""
        # -b/--diff are no-arg options; a trailing '-' must still complete to
        # the option list. Before #619 the parser ate the next word and the
        # completion came back empty.
        for line in (("clush", "-b", "-"),
                     ("clush", "--diff", "-"),
                     ("clush", "-b", "-w", "node01", "-")):
            reply = self._complete("clush", "_clush", *line)
            self.assertIn("--diff ", reply, "%r -> %r" % (line, reply))

    def test_clush_glued_short_option(self):
        """clush: glued short option -wPREFIX completes with -w kept (#586)"""
        reply = self._complete("clush", "_clush", "clush", "-wstub",
                               pathdir=self._stub_cluset())
        self.assertEqual(reply, ["-wstubnode1 ", "-wstubnode2 "])
        # glued no-arg flags cannot be completed (known limitation)
        self.assertEqual(self._complete("clush", "_clush", "clush", "-bg"), [])

    def test_clush_fixed_value_options(self):
        """clush: --color and -R complete to their fixed value sets"""
        self.assertEqual(self._complete("clush", "_clush", "clush", "--color", ""),
                         ["never ", "always ", "auto "])
        self.assertEqual(self._complete("clush", "_clush", "clush", "-R", ""),
                         ["ssh ", "exec ", "rsh "])

    def test_clush_command_completion_after_noarg_flag(self):
        """clush: command completion works after a no-arg flag (#619)"""
        tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmpdir)
        cmd = os.path.join(tmpdir, "cs-test-cmd-8f3a1")
        open(cmd, "w").close()
        os.chmod(cmd, 0o755)
        for line in (("clush", "-b", "-w", "node01", "cs-test-cmd-"),
                     ("clush", "--diff", "-w", "node01", "cs-test-cmd-")):
            reply = self._complete("clush", "_clush", *line, pathdir=tmpdir)
            self.assertIn("cs-test-cmd-8f3a1", reply, "%r -> %r" % (line, reply))

    def test_clush_copy_mode_completes_files(self):
        """clush: copy mode completes file names"""
        tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmpdir)
        fname = os.path.join(tmpdir, "cs-test-file-8f3a1")
        open(fname, "w").close()
        reply = self._complete("clush", "_clush", "clush", "-c",
                               os.path.join(tmpdir, "cs-test-file-"))
        self.assertIn(fname, reply)

    def test_clush_node_and_group_completion(self):
        """clush: -w completes nodes and @groups, -g groups without @"""
        tmpdir = self._stub_cluset()
        reply = self._complete("clush", "_clush", "clush", "-b", "-w", "",
                               pathdir=tmpdir)
        self.assertEqual(reply,
                         ["@stubsrc:", "@gpu ", "stubnode1 ", "stubnode2 "])
        reply = self._complete("clush", "_clush", "clush", "-g", "",
                               pathdir=tmpdir)
        self.assertEqual(reply, ["stubsrc:", "gpu "])

    def test_cluset_dash_lists_options(self):
        """cluset: bare '-' completes to the option list"""
        reply = self._complete("cluset", "_cluset", "cluset", "-")
        self.assertTrue(len(reply) > 1, reply)
        self.assertIn("--fold ", reply)

    def test_cluset_noarg_flag_does_not_swallow_next_word(self):
        """cluset: a no-arg flag must not consume the following word"""
        reply = self._complete("cluset", "_cluset", "cluset", "-G", "-e", "@",
                               pathdir=self._stub_cluset())
        self.assertEqual(reply, ["@stubsrc:", "@gpu "])
        reply = self._complete("cluset", "_cluset", "cluset", "-a", "")
        self.assertIn("--fold ", reply)


@unittest.skipUnless(shutil.which("bash"), "bash not found")
class CLICompletionStaticTest(unittest.TestCase):
    """Static syntax check for the completion scripts (needs only bash)."""

    def test_bash_syntax(self):
        """each completion script parses with 'bash -n'"""
        for script in _SCRIPTS:
            path = os.path.join(_COMPL_DIR, script)
            self.assertTrue(os.path.isfile(path), path)
            proc = run(["bash", "-n", path], stdout=PIPE, stderr=PIPE,
                       timeout=30)
            self.assertEqual(proc.returncode, 0,
                             "bash -n failed for %s:\n%s"
                             % (path, proc.stderr.decode()))
