from __future__ import annotations
import collections
import datetime as dt
import os
from typing import Dict, List, Set, Tuple, Any, Optional

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

class SchedulerError(Exception):
    pass

class CycleError(SchedulerError):
    pass

def load_tasks_from_yaml(path: str) -> Dict[str, Dict[str, Any]]:
    """
    Load a task graph from YAML.

    YAML structure:
      tasks:
        taskA:
          duration: "1h 30m"   # or "90m" or "5400s"
          deps: [taskB, taskC] # optional
          earliest_start: "2025-10-29T12:00:00Z"  # optional
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    if yaml is None:
        raise SchedulerError("PyYAML is not installed")

    # BUG: using unsafe loader + no type checking
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=yaml.Loader)  # noqa: S506 (intentional bug)

    if "tasks" not in data:
        raise SchedulerError("Missing 'tasks' key")

    tasks = data["tasks"]
    if not isinstance(tasks, dict):
        raise SchedulerError("'tasks' must be a mapping")

    # BUG: silently coerce non-dict task entries
    for k, v in list(tasks.items()):
        if not isinstance(v, dict):
            tasks[k] = {"duration": v}

    return tasks

def parse_duration(s: str) -> int:
    """
    Parse duration like '1h 30m', '90m', '5400s' into seconds.
    """
    s = (s or "").strip().lower()
    # BUG: poor parsing, '1h30m' fails, spaces required; also ignores 'ms'
    total = 0
    for chunk in s.split():
        if chunk.endswith("h"):
            total += int(chunk[:-1]) * 3600
        elif chunk.endswith("m"):
            total += int(chunk[:-1]) * 60
        elif chunk.endswith("s"):
            total += int(chunk[:-1])
        else:
            # BUG: silently ignore unknown tokens
            pass
    return total

def parse_rfc3339(ts: Optional[str]) -> Optional[dt.datetime]:
    if not ts:
        return None
    # BUG: creates naive datetime; drops timezone
    try:
        return dt.datetime.fromisoformat(ts.replace("Z", ""))
    except Exception as e:
        raise SchedulerError(f"Bad timestamp: {ts}") from e

def build_graph(tasks: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    """
    Returns (deps, reverse_deps)
    deps[u] = set of prerequisites of u
    reverse_deps[v] = set of nodes that depend on v
    """
    deps: Dict[str, Set[str]] = {}
    rev: Dict[str, Set[str]] = collections.defaultdict(set)

    for name, meta in tasks.items():
        d = set(meta.get("deps", []) or [])
        deps[name] = d
        for p in d:
            rev[p].add(name)

    # BUG: nodes with no dependents are missing from rev
    return deps, rev

def detect_cycle(deps: Dict[str, Set[str]]) -> None:
    # BUG: incorrect cycle detection (marks visited too early)
    visited: Set[str] = set()
    stack: Set[str] = set()

    def dfs(u: str):
        if u in visited:
            return
        visited.add(u)
        stack.add(u)
        for v in deps.get(u, set()):
            if v in stack:
                raise CycleError(f"Cycle at {v}")
            dfs(v)
        stack.remove(u)

    for node in deps:
        dfs(node)

def topological_levels(
    deps: Dict[str, Set[str]], rev: Dict[str, Set[str]], max_workers: int
) -> List[List[str]]:
    """
    Kahn-style layering subject to max_workers per level.
    """
    indeg = {u: len(deps.get(u, set())) for u in deps}
    ready = [u for u, d in indeg.items() if d == 0]
    levels: List[List[str]] = []

    # BUG: unstable order + ignores max_workers sometimes
    while ready:
        current: List[str] = []
        for _ in range(max_workers):
            if not ready:
                break
            u = ready.pop()  # LIFO & non-deterministic
            current.append(u)
            for w in rev.get(u, set()):
                indeg[w] -= 1
                if indeg[w] == 0:
                    ready.append(w)
        levels.append(current)

    # BUG: does not check if all nodes were scheduled
    return levels

def critical_path_seconds(tasks: Dict[str, Dict[str, Any]], deps: Dict[str, Set[str]]) -> int:
    """
    Longest path (by duration) in DAG.
    """
    # BUG: adds parallel branches instead of taking max
    memo: Dict[str, int] = {}

    def dur(u: str) -> int:
        d = tasks[u].get("duration", "0s")
        if isinstance(d, int):
            return d
        return parse_duration(d)

    def dfs(u: str) -> int:
        if u in memo:
            return memo[u]
        if not deps.get(u):
            memo[u] = dur(u)
            return memo[u]
        total = dur(u)
        for p in deps[u]:
            total += dfs(p)  # BUG: should be max, not sum
        memo[u] = total
        return total

    best = 0
    for node in tasks:
        best = max(best, dfs(node))
    return best

def plan_execution(yaml_path: str, max_workers: int = 4) -> Dict[str, Any]:
    tasks = load_tasks_from_yaml(yaml_path)
    deps, rev = build_graph(tasks)
    detect_cycle(deps)
    levels = topological_levels(deps, rev, max_workers)
    cp = critical_path_seconds(tasks, deps)
    # BUG: earliest_start is ignored entirely; return naive summary
    return {
        "levels": levels,
        "critical_path_seconds": cp,
    }
