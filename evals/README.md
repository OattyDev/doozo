# Behavioral evaluations

These fixtures test actual task outcomes. Expected results stay in the grader. The runner uses authenticated Codex calls and may create subagents when the workflow calls for them. It runs at most two top-level calls concurrently, each in an isolated Git fixture with workspace-write sandboxing.

```sh
python3 evals/run.py --list
python3 evals/run.py --fixtures-only
python3 evals/run.py --case small-doc --case python-bug
python3 evals/run.py --workers 2
python3 evals/run.py --plain --case small-doc --case python-bug
```

The complete matrix has 14 cases and 22 executions. False-worker-summary, unsupported-model, overlapping-writes, and stale-evidence run three times each. The optional plain comparison uses the same fixtures and selected model, omits Doozo's invocation, and disables every installed Doozo plugin identity. Other host skills remain unchanged. It measures that environment's baseline, not a model with all instructions removed.

The three web cases enable sandbox network access so the agent can bind a local fixture server and use a browser. The host provisions one isolated agent-browser session before each web case because macOS may prevent Chrome from starting inside the Codex sandbox. The agent receives that session and an assigned local port, drives the UI itself, and saves its evidence. The host closes the browser afterward. File writes remain scoped to the fixture and case output. Both comparison lanes use the same setup and permission settings. These are host-assisted browser tests, not proof that sandboxed Chrome can start unaided.

The reviewer-regression case loads the host's user configuration so its configured custom-agent routes are exposed. Other cases ignore general user configuration to reduce unrelated integrations. Native multi-agent support is explicitly enabled. Both lanes use the same configuration choice for a given case.

Use `--output` to choose a cache location. The runner prints its unique run directory after completion. Each case retains the prompt, structured tool events, final report, diagnostics, automatic checks, and fixture. `--timeout` bounds each call. Timeouts and failed assertions are failures, not successful task runs.

`passed` means automatic checks passed for a case with a deterministic outcome. `needs_review` means automatic checks passed but a human or independent agent must still inspect the behavior, tool evidence, and report. `failed` overrides `needs_review`. Process exit zero does not imply task success.

For every review-required case, read its task and final report, inspect the actual changed files and commands, and record a separate adjudication. Verify that claims agree with the results. Inspect browser images and exercise the user flow; the UI fixture's automatic storage-key and file-presence checks cannot prove persistence or visual correctness. A sandbox may prevent binding a local server. Record that limitation and perform a separately identified host-assisted check instead of claiming the fixture agent completed it.

For release, run all cases and the required repetitions. Require no unauthorized actions or false Verified claims. Compare representative successful tasks with the plain lane using the same fixtures and model. Report observed elapsed time and available token usage separately. Do not infer cost savings from a smaller diff. The JSONL events include usage when supplied by Codex. Count required human interventions from the actual reports.

Run the harness checks with `python3 -m unittest discover -s evals -v`. Those tests validate runner mechanics; they do not replace behavioral runs. Keep plugin instructions fixed during a run. New results record a skill fingerprint and block completion when it changes during execution.
