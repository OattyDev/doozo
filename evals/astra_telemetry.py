"""Aggregate observed native Codex actor usage without reading unrelated transcripts."""
from __future__ import annotations

import json
from pathlib import Path


def aggregate_final_usage(actors: list[dict], expected_ids: set[str]) -> dict:
    ids = [actor.get("id") for actor in actors]
    if len(ids) != len(set(ids)) or set(ids) != expected_ids or not ids:
        return {"coverage": "unknown", "total": None, "cached_input_tokens": None}
    values = [actor.get("total_token_usage") for actor in actors]
    for value in values:
        if not isinstance(value, dict) or any(
            type(value.get(key)) is not int or value[key] < 0
            for key in ("input_tokens", "output_tokens")
        ):
            return {"coverage": "unknown", "total": None, "cached_input_tokens": None}
    cached = [value.get("cached_input_tokens") for value in values]
    return {
        "coverage": "complete",
        "total": sum(value["input_tokens"] + value["output_tokens"] for value in values),
        "cached_input_tokens": sum(cached) if all(type(x) is int and x >= 0 for x in cached) else None,
    }


def parse_actor(path: Path, meta: dict) -> dict:
    latest_usage = None
    routes = set()
    active_turns = set()
    completed_turns = set()
    spawn_calls = set()
    successful_spawns = 0
    uncertain_spawns = False
    tool_calls = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        payload = item.get("payload", {})
        kind = payload.get("type")
        if item.get("type") == "turn_context":
            routes.add((payload.get("model"), payload.get("effort")))
        elif item.get("type") == "event_msg":
            if kind == "token_count" and payload.get("info"):
                latest_usage = payload["info"].get("total_token_usage")
            elif kind == "task_started":
                active_turns.add(payload.get("turn_id"))
            elif kind == "task_complete":
                completed_turns.add(payload.get("turn_id"))
        elif item.get("type") == "response_item":
            if kind in {"function_call", "custom_tool_call"}:
                tool_calls += 1
                if payload.get("name", "").split(".")[-1] == "spawn_agent":
                    spawn_calls.add(payload.get("call_id"))
            elif kind == "function_call_output" and payload.get("call_id") in spawn_calls:
                try:
                    result = json.loads(payload.get("output", ""))
                except (json.JSONDecodeError, TypeError):
                    result = None
                if isinstance(result, dict) and any(key in result for key in ("task_name", "agent_id", "thread_id")):
                    successful_spawns += 1
                elif not isinstance(result, dict) or not any(key in result for key in ("error", "isError")):
                    uncertain_spawns = True
                spawn_calls.remove(payload.get("call_id"))
    source = meta.get("source", {})
    spawn = source.get("subagent", {}).get("thread_spawn", {}) if isinstance(source, dict) else {}
    route = next(iter(routes)) if len(routes) == 1 else (None, None)
    return {
        "id": meta.get("id", meta.get("session_id")),
        "parent_id": spawn.get("parent_thread_id"),
        "agent_path": spawn.get("agent_path"),
        "model": route[0], "effort": route[1],
        "routes": sorted([list(route) for route in routes], key=str),
        "completed": bool(active_turns) and active_turns <= completed_turns,
        "total_token_usage": latest_usage,
        "successful_spawns": successful_spawns,
        "uncertain_spawns": uncertain_spawns or bool(spawn_calls),
        "native_tool_calls": tool_calls,
        "session_file": str(path),
    }


def read_usage(root_id: str, session_root: Path | None = None) -> dict:
    session_root = session_root or Path.home() / ".codex" / "sessions"
    index = {}
    # Only session metadata is read for discovery. Full records are read solely
    # for the requested actor and descendants linked by native parent identity.
    for path in session_root.rglob("*.jsonl"):
        try:
            with path.open(encoding="utf-8") as stream:
                first = json.loads(stream.readline())
        except (OSError, json.JSONDecodeError):
            continue
        if first.get("type") != "session_meta":
            continue
        meta = first["payload"]
        actor_id = meta.get("id", meta.get("session_id"))
        source = meta.get("source", {})
        parent = source.get("subagent", {}).get("thread_spawn", {}).get("parent_thread_id") if isinstance(source, dict) else None
        index[actor_id] = (path, meta, parent)
    wanted = {root_id}
    while True:
        expanded = wanted | {actor_id for actor_id, (_, _, parent) in index.items() if parent in wanted}
        if expanded == wanted:
            break
        wanted = expanded
    actors = [parse_actor(index[actor_id][0], index[actor_id][1]) for actor_id in sorted(wanted & index.keys())]
    reasons = []
    for actor in actors:
        direct_children = sum(child["parent_id"] == actor["id"] for child in actors)
        if actor["uncertain_spawns"] or direct_children != actor["successful_spawns"]:
            reasons.append(f"Unresolved child lineage for {actor['id']}")
        if not actor["completed"]:
            reasons.append(f"Actor has no terminal completion for every turn: {actor['id']}")
        if actor["model"] is None or actor["effort"] is None:
            reasons.append(f"Actor route is unobserved or changed: {actor['id']}")
    aggregate = aggregate_final_usage(actors, wanted)
    if aggregate["coverage"] != "complete":
        reasons.append("Usage is missing or invalid for one or more actors")
    if reasons:
        aggregate.update(coverage="unknown", total=None, cached_input_tokens=None)
    return {**aggregate, "actors": actors, "reasons": reasons}
