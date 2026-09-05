---
name: doo
description: Run a bounded repository change from scope through implementation and evidence-backed verification. Use for concrete fixes, features, and user-flow or artifact checks; follow explicit plan, grill, review, verify, or resume directions without expanding scope.
---

# Doo

Own the requested outcome through implementation, review when the risk warrants it, and current evidence. Keep the task within the user's scope and the repository's conventions.

## Route the request

At the start, read the task, repository instructions, current changes, and effective Doozo settings. Record the requested result and the observable checks that would demonstrate it. Preserve unrelated work.

Resolve the installed plugin root from this skill's location. Run `python3 <plugin-root>/scripts/setup.py resolve --compact` using the target project as the working directory, so its `.doozo/config.json` is included. Treat the returned JSON as the settings source for every route below. Pass explicit per-task settings with `--invocation-json` when the user selected an override. Reading settings does not authorize applying or rewriting them.

Use the smallest route that fits:

- For a small, low-risk task with clear acceptance criteria, known edit scope, and a focused check, use the fast path below.
- Other ordinary execution reads [execution.md](references/execution.md), then applies the relevant specialist reference.
- doo plan reads [design.md](references/design.md) and returns a design with acceptance checks. Stop before implementation until the user asks to proceed.
- doo grill reads [design.md](references/design.md) and runs the full dependency-aware interview. Investigate facts yourself, ask the frontier in rounds with recommendations, and wait for the user's confirmation before implementation.
- doo review reads [review.md](references/review.md) and reviews the requested baseline or working tree without silently implementing findings.
- doo verify reads [verification.md](references/verification.md) and exercises the requested path or artifact. Report what the evidence proves.
- doo resume reads [execution.md](references/execution.md) and [verification.md](references/verification.md), loads the saved checkpoint and evidence, rechecks live state, then continues.

Read [debugging.md](references/debugging.md) for a bug, failure, stack trace, or request to diagnose. Read [design.md](references/design.md) when terminology, state transitions, interfaces, or a consequential design choice needs work. Read [review.md](references/review.md) for a fresh correctness review. Read [verification.md](references/verification.md) when the result is a user flow, API, CLI, download, screenshot, or other artifact.

## Fast path

Keep the work with the parent: inspect relevant source and current changes, make the bounded edit, run the focused acceptance check, inspect the final state, and report the result. This route needs no separate plan, worker, or evidence ledger. Load specialist guidance only when its condition above applies; execution.md is unnecessary here.

Use the full execution route if scope or acceptance is uncertain, a failed check exposes a wider problem, or independent review is required. Independent review is required for substantial changes, authentication/authorization, financial calculations, concurrent state, data migrations, destructive operations, and explicit user requests; quality-first also requires it for every code change. Stop checking after required checks pass unless new changes or unresolved evidence justify another check.

## Operating boundaries

Ordinary execution asks only questions whose answer would materially change the result, while independent investigation continues. The full design interview belongs to explicit grill mode. A plan or review request keeps its scope and does not silently become implementation or deployment.

Role selection and ownership follow [execution.md](references/execution.md) when delegating. Browser selection follows [verification.md](references/verification.md) when using a browser.

Do not send external messages, deploy, publish, delete data, or make another irreversible change without the required user authorization. Do not claim a speculative fix is verified. A missing reproduction, required access, or current acceptance check leaves the result incomplete or blocked.

## Completion

Report the changed behavior, changed files, commands and results, actual artifacts or screenshots when useful, review disposition, and unresolved limitations. Use these meanings:

- **Verified** means every required acceptance check has current evidence and no required review finding remains unresolved.
- **Incomplete** means work exists but a required check, implementation step, or review remains unfinished.
- **Blocked** means a concrete external dependency prevents progress; name what is needed.

The parent agent owns integration and the final claim. Inspect the actual final state after any review fix. For substantial work, keep the evidence records described in [verification.md](references/verification.md).
