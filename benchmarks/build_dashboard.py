#!/usr/bin/env python3
"""Build the custom ClusterShell dashboard from ASV result files."""

import argparse
import datetime
import hashlib
import itertools
import json
import math
import shutil
import subprocess
from pathlib import Path


def read_json(path):
    """Read an ASV JSON file."""
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def git_output(project_root, *args):
    """Return stripped git output, or an empty string for unknown commits."""
    try:
        return subprocess.check_output(
            ["git", *args], cwd=str(project_root), stderr=subprocess.DEVNULL,
            text=True).strip()
    except subprocess.CalledProcessError:
        return ""


def commit_metadata(project_root, commit_hash, timestamp):
    """Return presentation metadata for a benchmarked commit."""
    tags = git_output(project_root, "tag", "--points-at", commit_hash).splitlines()
    master_hash = git_output(project_root, "rev-parse", "master")
    if master_hash == commit_hash and "master" not in tags:
        tags.append("master")
    subject = git_output(project_root, "show", "-s", "--format=%s", commit_hash)
    return {
        "hash": commit_hash,
        "shortHash": commit_hash[:8],
        "date": timestamp,
        "subject": subject,
        "tags": sorted(tags),
        "url": "https://github.com/clustershell/clustershell/commit/" + commit_hash,
    }


def finite_value(value):
    """Return finite numeric values only."""
    if isinstance(value, (int, float)) and math.isfinite(value):
        return value
    return None


def result_column(raw_result, column_index, name, default=None):
    """Read one result column; asv writes short rows for failed benchmarks."""
    index = column_index.get(name, len(raw_result))
    return raw_result[index] if index < len(raw_result) else default


def parameter_combinations(benchmark):
    """Expand ASV parameter axes in the same order as result values."""
    axes = benchmark.get("params") or []
    names = benchmark.get("param_names") or []
    if not axes:
        return [({}, "default")]

    combinations = []
    for values in itertools.product(*axes):
        parameters = dict(zip(names, values))
        label = ", ".join("%s=%s" % item for item in parameters.items())
        combinations.append((parameters, label))
    return combinations


def benchmark_group(name):
    """Map benchmark module names to user-facing groups."""
    if name.startswith("bench_rangeset."):
        return "RangeSet"
    if name.startswith("bench_nodeset."):
        return "NodeSet"
    if name.startswith("bench_msgtree."):
        return "MsgTree"
    if name.startswith("bench_imports."):
        return "Imports"
    if name.startswith("bench_engine."):
        return "Engine"
    if name.startswith("bench_output."):
        return "Output"
    return "Other"


def benchmark_label(name):
    """Return a compact public name without ASV's module prefix."""
    parts = name.split(".")
    return "%s.%s" % (benchmark_group(name), parts[-1])


def build_model(results_dir, project_root):
    """Convert ASV's storage format into the dashboard's stable model."""
    benchmark_path = results_dir / "benchmarks.json"
    if not benchmark_path.exists():
        raise SystemExit("Missing ASV benchmark metadata: %s" % benchmark_path)

    metadata = read_json(benchmark_path)
    benchmarks = {}
    for name, definition in metadata.items():
        if not isinstance(definition, dict):
            continue
        # only duration benchmarks are rendered; others stay in the ASV view
        if definition.get("unit", "seconds") != "seconds":
            continue
        benchmarks[name] = {
            "id": name,
            "group": benchmark_group(name),
            "label": benchmark_label(name),
            "operation": name.split(".")[-1],
            "unit": definition.get("unit", "seconds"),
            "parameterNames": definition.get("param_names") or [],
            "series": {},
        }

    machines = {}
    commit_cache = {}
    latest_started_at = 0

    for path in sorted(results_dir.glob("*/*.json")):
        if path.name == "machine.json":
            continue
        result_file = read_json(path)
        commit_hash = result_file.get("commit_hash")
        if not commit_hash:
            continue

        columns = result_file.get("result_columns") or []
        column_index = {name: index for index, name in enumerate(columns)}
        params = result_file.get("params") or {}
        machine_name = params.get("machine", path.parent.name)
        python_version = str(result_file.get("python") or params.get("python") or "")
        environment = result_file.get("env_name", "")
        machine_key = "%s|%s|%s" % (machine_name, python_version, environment)
        machine_id = hashlib.sha1(machine_key.encode("utf-8")).hexdigest()[:12]
        machines[machine_id] = {
            "id": machine_id,
            "name": machine_name,
            "python": python_version,
            "environment": environment,
            "cpu": params.get("cpu", ""),
            "os": params.get("os", ""),
            "arch": params.get("arch", ""),
        }

        timestamp = result_file.get("date")
        if commit_hash not in commit_cache:
            commit_cache[commit_hash] = commit_metadata(
                project_root, commit_hash, timestamp)

        for name, raw_result in (result_file.get("results") or {}).items():
            if name not in benchmarks or "result" not in column_index:
                continue
            values = raw_result[column_index["result"]]
            if not isinstance(values, list):
                values = [values]
            q25_values = result_column(raw_result, column_index,
                                       "stats_q_25") or []
            q75_values = result_column(raw_result, column_index,
                                       "stats_q_75") or []
            started_at = result_column(raw_result, column_index, "started_at")
            latest_started_at = max(latest_started_at, started_at or 0)

            combinations = parameter_combinations(metadata[name])
            for index, (parameters, parameter_label) in enumerate(combinations):
                if index >= len(values) or finite_value(values[index]) is None:
                    continue
                series_key = "%s|%s" % (machine_id, parameter_label)
                series = benchmarks[name]["series"].setdefault(series_key, {
                    "id": hashlib.sha1(
                        (name + "|" + series_key).encode("utf-8")
                    ).hexdigest()[:16],
                    "machineId": machine_id,
                    "parameters": parameters,
                    "parameterLabel": parameter_label,
                    "points": [],
                })
                point = dict(commit_cache[commit_hash])
                point.update({
                    "value": values[index],
                    "lower": finite_value(q25_values[index])
                    if index < len(q25_values) else None,
                    "upper": finite_value(q75_values[index])
                    if index < len(q75_values) else None,
                    "startedAt": started_at,
                })
                series["points"].append(point)

    # sort by position on master: author dates are not monotonic under rebases
    history = git_output(project_root, "rev-list", "--first-parent",
                         "--reverse", "master").splitlines()
    position = {commit: index for index, commit in enumerate(history)}

    def point_order(point):
        if point["hash"] in position:
            return (0, position[point["hash"]])
        return (1, point.get("date") or 0)

    output_benchmarks = []
    for benchmark in benchmarks.values():
        benchmark["series"] = list(benchmark["series"].values())
        for series in benchmark["series"]:
            series["points"].sort(key=point_order)
        if benchmark["series"]:
            output_benchmarks.append(benchmark)
    output_benchmarks.sort(key=lambda item: (item["group"], item["operation"]))

    generated_at = None
    if latest_started_at:
        generated_at = datetime.datetime.fromtimestamp(
            latest_started_at / 1000, tz=datetime.timezone.utc).isoformat()

    return {
        "project": {
            "name": "ClusterShell",
            "repositoryUrl": "https://github.com/clustershell/clustershell",
            "asvUrl": "asv/",
        },
        "generatedAt": generated_at,
        "machines": sorted(machines.values(), key=lambda item: item["name"]),
        "benchmarks": output_benchmarks,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=Path(".asv/results"))
    parser.add_argument("--output", type=Path,
                        default=Path(".asv/custom-dashboard"))
    parser.add_argument("--project-root", type=Path, default=Path("."))
    args = parser.parse_args()

    source_dir = Path(__file__).resolve().parent / "dashboard"
    args.output.mkdir(parents=True, exist_ok=True)
    for source in source_dir.iterdir():
        if source.is_file():
            shutil.copy2(source, args.output / source.name)

    model = build_model(args.results.resolve(), args.project_root.resolve())
    with (args.output / "data.json").open("w", encoding="utf-8") as stream:
        json.dump(model, stream, indent=2, allow_nan=False)
        stream.write("\n")


if __name__ == "__main__":
    main()
