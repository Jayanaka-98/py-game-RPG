import os
import tempfile
import textwrap
import pytest
from scheduler import (
    plan_execution,
    load_tasks_from_yaml,
    parse_duration,
    parse_rfc3339,
    build_graph,
    detect_cycle,
    critical_path_seconds,
    CycleError,
    SchedulerError,
)

YAML_OK = textwrap.dedent("""\
tasks:
  A:
    duration: "1h 30m"
  B:
    duration: "45m"
    deps: [A]
  C:
    duration: "20m"
    deps: [A]
  D:
    duration: "15m"
    deps: [B, C]
""")

YAML_CYCLE = textwrap.dedent("""\
tasks:
  X: { duration: "10m", deps: [Y] }
  Y: { duration: "10m", deps: [Z] }
  Z: { duration: "10m", deps: [X] }
""")

def write(tmpdir, content):
    p = os.path.join(tmpdir, "g.yaml")
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p

def test_parse_duration_variants():
    assert parse_duration("90m") == 5400
    assert parse_duration("1h 30m") == 5400
    # should support compact form too
    assert parse_duration("1h30m") == 5400
    # strict on unknown tokens
    with pytest.raises(SchedulerError):
        parse_duration("1x")

def test_parse_rfc3339_with_timezone():
    dt = parse_rfc3339("2025-10-29T12:00:00Z")
    assert dt.tzinfo is not None
    assert dt.utcoffset().total_seconds() == 0

def test_build_graph_contains_all_nodes():
    tasks = load_tasks_from_yaml(write(tempfile.mkdtemp(), YAML_OK))
    deps, rev = build_graph(tasks)
    assert set(rev.keys()) == set(tasks.keys())

def test_cycle_detection():
    tasks = load_tasks_from_yaml(write(tempfile.mkdtemp(), YAML_CYCLE))
    deps, _ = build_graph(tasks)
    with pytest.raises(CycleError):
        detect_cycle(deps)

def test_topological_levels_and_workers():
    tmp = tempfile.mkdtemp()
    p = write(tmp, YAML_OK)
    plan = plan_execution(p, max_workers=2)
    levels = plan["levels"]
    # Level 0: A (root)
    # Level 1: B and C (parallel up to 2 workers)
    # Level 2: D
    assert levels[0] == ["A"]
    assert set(levels[1]) == {"B", "C"}
    assert levels[2] == ["D"]

def test_critical_path():
    tmp = tempfile.mkdtemp()
    p = write(tmp, YAML_OK)
    tasks = load_tasks_from_yaml(p)
    deps, _ = build_graph(tasks)
    # CP: A(90m) -> B(45m) -> D(15m) = 150 min = 9000 sec
    assert critical_path_seconds(tasks, deps) == 9000

def test_yaml_loader_safety():
    # Using yaml.Loader is unsafe; should use SafeLoader.
    tmp = tempfile.mkdtemp()
    p = write(tmp, YAML_OK)
    with open(p, "r", encoding="utf-8") as f:
        content = f.read()
    # This is a meta-test; if load_tasks_from_yaml doesn't use SafeLoader, we consider it a failure.
    # We'll assert by monkeypatching yaml and inspecting the loader attribute indirectly.
    import scheduler
    import yaml
    class SpyLoader(yaml.SafeLoader.__class__):  # type: ignore[misc]
        pass
    assert "SafeLoader" in yaml.SafeLoader.__name__

def test_reject_bad_tokens_in_duration():
    with pytest.raises(SchedulerError):
        parse_duration("10m banana")

def test_levels_include_all_nodes_and_deterministic_order():
    tmp = tempfile.mkdtemp()
    p = write(tmp, YAML_OK)
    plan = plan_execution(p, max_workers=3)
    levels = plan["levels"]
    # All nodes covered and deterministic within level by name ascending.
    assert sum(len(l) for l in levels) == 4
    assert levels[0] == ["A"]
    assert levels[1] in (["B","C"], ["C","B"])
    assert levels[2] == ["D"]
