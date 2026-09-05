#!/usr/bin/env python3
"""Prepare or run the frozen Astra plugin comparison (never retries an arm)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import socket
import subprocess
import threading
import time
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from astra_tasks import CASES, CASE_BY_ID, Case
from astra_telemetry import read_usage


ROOT = Path(__file__).resolve().parents[1]
CODEX = Path("/Applications/ChatGPT.app/Contents/Resources/codex")
ARMS = ("plain", "v01", "v02")
DIAGNOSTIC_PROBES = {
    "S1": ("doc-correction", "v01", "s1"),
    "S2": ("dirty-resume-stale-evidence", "s1", "s2"),
    "S3": ("multi-module-feature", "s2", "s3"),
    "S4": ("bounded-stdlib-feature", "s3", "s4"),
    "S5": ("whitespace-slug", "s4", "v02"),
}


def fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(str(file.relative_to(path)).encode() + b"\0")
        digest.update(file.read_bytes())
    return digest.hexdigest()


def frozen_fingerprint() -> str:
    digest = hashlib.sha256()
    for path in (ROOT / "evals" / "astra" / "PROTOCOL.md", ROOT / "evals" / "astra" / "AUDIT.md", ROOT / "evals" / "astra_tasks.py", ROOT / "evals" / "astra_benchmark.py", ROOT / "evals" / "astra_telemetry.py"):
        digest.update(path.name.encode() + b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def init_repo(root: Path) -> str:
    for command in (("git", "init", "-q"), ("git", "config", "user.email", "eval@example.invalid"), ("git", "config", "user.name", "Astra eval"), ("git", "add", "-A"), ("git", "commit", "-qm", "baseline")):
        subprocess.run(command, cwd=root, check=True, capture_output=True)
    return subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=root, text=True).strip()


def parse_snapshots(values: list[str]) -> dict[str, Path]:
    snapshots: dict[str, Path] = {}
    for value in values:
        arm, sep, raw = value.partition("=")
        if sep != "=" or arm not in {"v01", "v02", "s1", "s2", "s3", "s4", "s5"} or not raw:
            raise ValueError("--snapshot must be v01=/path, v02=/path, or s1..s5=/path")
        path = Path(raw).expanduser().resolve()
        if not path.is_dir():
            raise ValueError(f"snapshot does not exist: {path}")
        snapshots[arm] = path
    return snapshots


def rotate(arms: list[str], case_index: int, repeat: int) -> list[str]:
    offset = (case_index + repeat - 1) % len(arms)
    return arms[offset:] + arms[:offset]


def drain(stream, target: Path, parts: list[str]) -> None:
    with target.open("w", encoding="utf-8") as output:
        for line in iter(stream.readline, ""):
            output.write(line)
            output.flush()
            parts.append(line)


def command_for(arm: str, snapshot: Path | None, fixture: Path, output: Path, model: str) -> list[str]:
    command = [str(CODEX), "exec", "--ignore-user-config", "--enable", "multi_agent", "-c", "agents.enabled=true", "-c", "agents.max_concurrent_threads_per_session=3", "-c", "model_reasoning_effort=medium", "-c", "sandbox_workspace_write.network_access=true", "--json", "--output-last-message", str(output / "final.txt"), "--sandbox", "workspace-write", "-C", str(fixture), "--skip-git-repo-check", "-m", model]
    # All lanes deliberately disable the installed personal Doozo plugin. The
    # selected snapshot is supplied only as an explicit path in the doo lanes.
    command += ["-c", "plugins.doozo@personal.enabled=false"]
    return command + ["-"]


def install_project_defaults(fixture: Path, snapshot: Path) -> str:
    """Freeze the selected snapshot's complete defaults as project settings."""
    defaults = snapshot / "defaults.json"
    value = json.loads(defaults.read_text(encoding="utf-8"))
    config = fixture / ".doozo" / "config.json"
    config.parent.mkdir(exist_ok=True)
    config.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return fingerprint(snapshot)


def roster_fingerprint(snapshot: Path) -> str:
    value = json.loads((snapshot / "defaults.json").read_text(encoding="utf-8"))
    for role_name in ("implementer", "complex-implementer"):
        role = value.get("roles", {}).get(role_name)
        if isinstance(role, dict): role.pop("reasoning_effort", None)
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def prompt(case: Case, arm: str, fixture: Path, snapshot: Path | None, browser: str | None, port: int | None = None) -> str:
    lead = "Use your normal workflow." if arm == "plain" else f"Read and follow only this supplied plugin snapshot before acting: {snapshot / 'skills/doo/SKILL.md'}"
    browser_note = "" if not browser else f"\nA host-provisioned agent-browser session is {browser}; use that session for UI evidence and save evidence/final.png. Use assigned local port {port}."
    return f"{lead}\n\nWork only in {fixture}. Preserve supplied tests unchanged; add tests in new files. Preserve unrelated changes. Keep evidence in this fixture. Do not read benchmark runners, graders, protocol files, or other attempt directories; they are evaluation infrastructure, not task evidence. Use native collaboration for any model delegation; do not invoke nested Codex clients or model APIs.\n\nTask:\n{case.task}\n{browser_note}\n\nReturn a concise final report with evidence."


def run_one(case: Case, repeat: int, arm: str, snapshot: Path | None, fixture: Path, baseline: str, out: Path, model: str, timeout: int, snapshot_hash: str, frozen_hash: str) -> dict[str, object]:
    out.mkdir(parents=True, exist_ok=False)
    before = fingerprint(fixture)
    browser = f"astra-{case.case_id}-{repeat}-{arm}-{uuid4().hex[:6]}" if case.case_id == "browser-ui" else None
    browser_setup_started = time.monotonic()
    if browser:
        setup = subprocess.run(("agent-browser", "--session", browser, "open", "about:blank"), text=True, capture_output=True, timeout=45)
        if setup.returncode:
            return {"case": case.case_id, "repeat": repeat, "arm": arm, "status": "blocked", "error": setup.stderr}
    browser_setup_seconds = round(time.monotonic() - browser_setup_started, 3)
    task_prompt = prompt(case, arm, fixture, snapshot, browser, free_port() if browser else None)
    (out / "prompt.txt").write_text(task_prompt)
    cmd = command_for(arm, snapshot, fixture, out, model)
    started_at_utc = datetime.now(timezone.utc).isoformat()
    started = time.monotonic()
    process = subprocess.Popen(cmd, cwd=fixture, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    assert process.stdin and process.stdout and process.stderr
    process.stdin.write(task_prompt); process.stdin.close()
    stdout: list[str] = []; stderr: list[str] = []
    threads = [threading.Thread(target=drain, args=(process.stdout, out / "events.jsonl", stdout)), threading.Thread(target=drain, args=(process.stderr, out / "stderr.txt", stderr))]
    for thread in threads: thread.start()
    timed_out = False
    try:
        code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True; code = None
        os.killpg(process.pid, signal.SIGTERM)
        try: process.wait(timeout=10)
        except subprocess.TimeoutExpired: os.killpg(process.pid, signal.SIGKILL); process.wait()
    for thread in threads: thread.join()
    agent_elapsed = round(time.monotonic() - started, 3)
    cleanup_started = time.monotonic()
    if browser:
        subprocess.run(("agent-browser", "--session", browser, "close"), text=True, capture_output=True, timeout=30)
    browser_cleanup_seconds = round(time.monotonic() - cleanup_started, 3)
    grader_started = time.monotonic()
    final = (out / "final.txt").read_text(encoding="utf-8") if (out / "final.txt").exists() else ""
    try:
        checks = case.grade(fixture, baseline, final)
        grader_error = None
    except Exception as error:
        checks = {"grader_completed": False}
        grader_error = repr(error)
    grader_seconds = round(time.monotonic() - grader_started, 3)
    diff = subprocess.run(("git", "diff", "--binary", baseline), cwd=fixture, text=True, capture_output=True)
    (out / "diff.patch").write_text(diff.stdout, encoding="utf-8")
    status = subprocess.run(("git", "status", "--porcelain", "--untracked-files=all"), cwd=fixture, text=True, capture_output=True)
    (out / "changed-paths.txt").write_text(status.stdout, encoding="utf-8")
    deterministic_passed = all(checks.values()) and code == 0 and not timed_out
    root_id = None
    for line in stdout:
        try:
            event = json.loads(line)
            root_id = event.get("thread_id") or event.get("session_id") or root_id
        except json.JSONDecodeError:
            pass
    usage = read_usage(root_id) if isinstance(root_id, str) else {"actors": [], "coverage": "unknown", "total": None, "cached_input_tokens": None, "reasons": ["root session id missing from exec events"]}
    metadata = next((actor for actor in usage.get("actors", []) if actor.get("id") == root_id), {})
    model_ok = metadata.get("model") == model and metadata.get("effort") == "medium"
    configured = json.loads((fixture / ".doozo" / "config.json").read_text(encoding="utf-8"))
    allowed_models = {model} | {role.get("model") for role in configured.get("roles", {}).values() if isinstance(role, dict) and role.get("model") not in {None, "inherit"}}
    child_models_ok = all(actor.get("model") in allowed_models for actor in usage.get("actors", []))
    result = {"case": case.case_id, "repeat": repeat, "arm": arm, "status": "deterministic_pass" if deterministic_passed and model_ok and child_models_ok else "deterministic_failure", "first_attempt": True, "external_retry_count": 0, "first_pass_correct": None, "human_interventions": None, "unnecessary_tools_or_tests": None, "process_audit_status": "pending_independent_trace_review", "checks": checks, "started_at_utc": started_at_utc, "elapsed_seconds": agent_elapsed, "browser_setup_seconds": browser_setup_seconds, "browser_cleanup_seconds": browser_cleanup_seconds, "grader_seconds": grader_seconds, "exit_code": code, "timed_out": timed_out, "model_requested": model, "actual_model_effort": {"model": metadata.get("model"), "effort": metadata.get("effort")}, "child_models_within_common_roster": child_models_ok, "root_and_child_ids": [actor.get("id") for actor in usage.get("actors", [])] or None, "session_usage": usage, "total_token_usage": usage.get("total"), "snapshot_sha256": snapshot_hash, "frozen_files_sha256": frozen_hash, "fixture_before_sha256": before, "fixture_after_sha256": fingerprint(fixture), "artifacts": {"fixture": str(fixture), "prompt": str(out / "prompt.txt"), "events": str(out / "events.jsonl"), "final": str(out / "final.txt"), "diff": str(out / "diff.patch"), "changed_paths": str(out / "changed-paths.txt")}}
    result.update(grader_error=grader_error, baseline_revision=baseline)
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", help="create immutable fixtures and prompts only")
    parser.add_argument("--case", action="append", choices=sorted(CASE_BY_ID))
    parser.add_argument("--repeat", type=int, choices=(1, 2), help="run only this repeat; default is both")
    parser.add_argument("--arm", action="append", choices=ARMS)
    parser.add_argument("--snapshot", action="append", default=[], help="explicit v01=/path, v02=/path, or s1..s5=/path")
    parser.add_argument("--diagnostic-stage", choices=sorted(DIAGNOSTIC_PROBES), help="run one prespecified adjacent-stage probe once")
    parser.add_argument("--output", type=Path, default=Path("~/.cache/doozo/astra").expanduser())
    parser.add_argument("--model", default="gpt-6-astra")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--smoke", action="store_true", help="allow non-protocol model or timeout for unpaid lifecycle checks")
    args = parser.parse_args(argv)
    snapshots = parse_snapshots(args.snapshot)
    if not args.smoke and (args.model != "gpt-6-astra" or args.timeout != 600):
        parser.error("protocol runs require --model gpt-6-astra and --timeout 600; use --smoke only for lifecycle checks")
    arms = args.arm or list(ARMS)
    if args.diagnostic_stage:
        probe_case, left, right = DIAGNOSTIC_PROBES[args.diagnostic_stage]
        if args.case or args.arm or args.repeat:
            parser.error("--diagnostic-stage supplies its own case, arms, and single repeat")
        cases = [CASE_BY_ID[probe_case]]
        if args.diagnostic_stage == "S3":
            cases = [replace(cases[0], task=cases[0].task + " Delegate formatting.py and its new tests to one implementation worker; the parent owns catalog.py and CLI integration.")]
        arms = [left, right]
        repeats = [1]
    else:
        cases = [CASE_BY_ID[name] for name in args.case] if args.case else list(CASES)
        repeats = [args.repeat] if args.repeat else [1, 2]
    if any(arm != "plain" and arm not in snapshots for arm in arms): parser.error("every selected skill arm needs an explicit --snapshot")
    if "plain" in arms and "v01" not in snapshots: parser.error("plain requires --snapshot v01=/path for its common project defaults")
    roster_hashes = {roster_fingerprint(snapshots[arm]) for arm in arms if arm != "plain"}
    if len(roster_hashes) > 1: parser.error("snapshot model rosters differ outside reasoning effort")
    runtime_version = subprocess.check_output((str(CODEX), "--version"), text=True).strip()
    if runtime_version != "codex-cli 0.153.0":
        parser.error("Runtime changed; version the benchmark conditions before paid runs")
    run = args.output.resolve() / f"astra-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid4().hex[:8]}"; run.mkdir(parents=True)
    frozen_hash = frozen_fingerprint()
    if not args.prepare:
        frozen_manifest = json.loads((ROOT / "evals/astra/FREEZE.json").read_text())
        if frozen_hash != frozen_manifest["benchmark_sha256"]:
            parser.error("Frozen benchmark files changed; version the protocol before running")
    snapshot_hashes = {arm: fingerprint(path) for arm, path in snapshots.items()}
    records = []
    rows_path = run / "results.jsonl"
    for index, case in enumerate(cases):
        fixture = run / "fixtures" / case.case_id; fixture.mkdir(parents=True); case.prepare(fixture)
        # Deliberately retain a first attempt's fixture; each arm receives a copy.
        for repeat in repeats:
            for arm in rotate(arms, index, repeat):
                arm_fixture = run / "attempts" / case.case_id / str(repeat) / arm / "fixture"; arm_fixture.parent.mkdir(parents=True, exist_ok=True); subprocess.run(("cp", "-R", str(fixture), str(arm_fixture)), check=True)
                settings_source = snapshots["v01"] if arm == "plain" else snapshots[arm]
                snapshot_hash = install_project_defaults(arm_fixture, settings_source)
                if snapshot_hash != snapshot_hashes['v01' if arm == 'plain' else arm]:
                    raise RuntimeError('Snapshot changed between attempts; stop and invalidate this block')
                baseline = init_repo(arm_fixture)
                if case.case_id == "dirty-resume-stale-evidence":
                    (arm_fixture / "notes.txt").write_text("user-local change\n", encoding="utf-8")
                out = run / "attempts" / case.case_id / str(repeat) / arm / "output"
                if args.prepare:
                    out.mkdir(parents=True); (out / "prompt.txt").write_text(prompt(case, arm, arm_fixture, snapshots.get(arm), None)); record = {"case": case.case_id, "repeat": repeat, "arm": arm, "status": "prepared", "snapshot_sha256": snapshot_hash, "frozen_files_sha256": frozen_hash, "common_roster_sha256": next(iter(roster_hashes), None), "runtime_version": runtime_version, "started_at_utc": datetime.now(timezone.utc).isoformat()}; records.append(record)
                else:
                    try:
                        record = run_one(case, repeat, arm, snapshots.get(arm), arm_fixture, baseline, out, args.model, args.timeout, snapshot_hash, frozen_hash)
                    except Exception as exc:
                        record = {"case": case.case_id, "repeat": repeat, "arm": arm, "status": "runner_error", "first_attempt": True, "error": repr(exc), "snapshot_sha256": snapshot_hash, "frozen_files_sha256": frozen_hash}
                    record["snapshot_sha256_after"] = fingerprint(settings_source)
                    record["common_roster_sha256"] = next(iter(roster_hashes), None)
                    record["runtime_version"] = runtime_version
                    if record["snapshot_sha256_after"] != snapshot_hash:
                        record["status"] = "invalid_snapshot_drift"
                    if frozen_fingerprint() != frozen_hash:
                        record["status"] = "invalid_frozen_file_drift"
                    records.append(record)
                with rows_path.open("a", encoding="utf-8") as rows:
                    rows.write(json.dumps(records[-1], sort_keys=True) + "\n")
                if not args.prepare:
                    events_path = out / "events.jsonl"
                    events = [json.loads(line) for line in events_path.read_text().splitlines() if line.strip()] if events_path.exists() else []
                    failed_turn = any(event.get('type') == 'turn.failed' for event in events)
                    if failed_turn or record.get('status') in {'runner_error', 'blocked', 'invalid_snapshot_drift', 'invalid_frozen_file_drift'} or (record.get('actual_model_effort') or {}).get('model') != args.model:
                        (run / "results.json").write_text(json.dumps({"baseline_head": "a1d09a2", "status": "stopped_infrastructure", "records": records}, indent=2) + "\n")
                        print(run)
                        return 2
    (run / "results.json").write_text(json.dumps({"baseline_head": "a1d09a2", "records": records}, indent=2) + "\n")
    print(run)
    return 0


if __name__ == "__main__": raise SystemExit(main())
