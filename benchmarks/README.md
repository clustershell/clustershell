# ClusterShell benchmarks

Performance benchmarks for ClusterShell, run with
[airspeed velocity](https://asv.readthedocs.io/) (`asv`). Each benchmarked
commit is built as a wheel and installed into an asv-managed virtualenv,
results are stored as JSON and can be published as a static HTML site with
per-benchmark charts across the commit history, making performance drift
between versions easy to spot.

## Setup

```console
$ pip install asv virtualenv
$ cd benchmarks
$ asv machine --yes        # one-time machine description
```

## Usage

Benchmark the tip of master:

```console
$ asv run master^!
```

Benchmark a released version, or a span of history:

```console
$ asv run v1.10.1^!
$ asv run --steps 10 v1.9.3..master
```

Compare two commits, or gate a working branch against master (fails on
regressions worse than 5%):

```console
$ asv compare v1.10.1 master
$ asv continuous -f 1.05 master HEAD
```

Browse the results as charts:

```console
$ asv publish
$ asv preview
```

Environments, results and HTML output live under `benchmarks/.asv/`
(git-ignored). Results are per-machine; see the asv documentation for
sharing and publishing them.

## Writing benchmarks

Benchmarks live in `benchmarks/benchmarks/` and follow the
[asv conventions](https://asv.readthedocs.io/en/stable/writing_benchmarks.html)
(`time_*`, `peakmem_*`, `timeraw_*` methods). The suite code from the current
checkout is run against older ClusterShell versions, so benchmarks must only
use long-stable public APIs, and mutating operations should rebuild their
state in the timed function itself.

Prebuilt benchmark state is defined at module level rather than in `setup()`
hooks: with a `setup()` hook, the pinned `asv_runner` (see `asv.conf.json`)
disables timeit batching and re-runs setup before every sample, which drowns
microsecond benchmarks in per-call overhead.
