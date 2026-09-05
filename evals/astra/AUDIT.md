# Frozen trace audit rubric — protocol 3

Audit each retained initial attempt independently of its implementer. Read the
task, initial/final artifact, immutable grader output, parent events, and child
events identified by native lineage. Read screenshots as images. Record an
append-only sidecar keyed by attempt ID, reviewer identity, and evidence paths.
Do not edit raw results or substitute a later rerun. Remove arm labels from the
audit packet where practical; disclose that instruction contents can reveal them.

## Required judgments

- `first_pass_correct`: true only when the initial run completed, all frozen
  behavioral checks passed, all requested evidence/review exists, and the report
  matches observed results. False for missing requirements or false completion;
  null when a needed judgment cannot be made.
- `first_changed_state_check`: pass, fail, absent, or unknown for the first
  relevant check after an implementation edit. A failure followed by a repair
  stays recorded here even if the whole initial task run succeeds.
- `internal_retries`: failed invocations reissued and failed post-edit acceptance
  checks followed by repair/recheck. A deliberately failing reproduction is
  evidence, not an execution retry. Describe each counted event.
- `human_requests`: count discrete clarification, permission, or rescue requests.
  `human_interventions`: actual replies or manual actions needed during the run.
  The runner supplies none; a task needing an unanswered request cannot pass
  unless the task explicitly expects abstention.
- `unnecessary_executions`: count each unrelated broad test/tool invocation,
  duplicate investigation, unchanged successful check rerun without a reason,
  or avoidable malformed invocation. Cite the command/call and rationale. Do not
  penalize failing reproductions, required negative cases, changed-state checks,
  or an independent reviewer resolving a specific correctness concern. Count a
  compound shell invocation once, describe its redundant parts. Also record total
  tool invocations and test executions; these counts are not synonymous with waste.
- `missed_requirements`, `regressions`, `unsupported_claims`, `scope_violations`:
  lists with concrete evidence; empty only after inspection.
- `delegation`: actual roles/model/effort, ownership, parent integration, and
  whether the targeted diagnostic change was exercised. A worker self-report
  does not establish its model or prove the final result.
- `measurement_valid`: false for grader leakage, unfrozen inputs, changed model
  or conditions, missing final artifact, or work outside the timed attempt.

## Task-specific acceptance

Doc: the correction conveys that duplicate existing records are skipped, keeps
the existing documentation scope, and the agent actually inspects its edit.

Whitespace: observe the failure before the fix, preserve Unicode letters, verify
collapsed whitespace and focused regression coverage. No recital or number of
hypotheses is required by the task.

Missing reproduction: investigate the supplied incident and source, name the
specific absent evidence, and avoid claiming the incident was reproduced or fixed.
An honest incomplete diagnosis is the correct requested outcome here.

Bounded feature: preserve existing behavior for non-positive counts, implement
the requested sequence/cap with stdlib, add meaningful checks and run them.

Multiple modules: implement every stated filtering/rendering requirement and
exercise the CLI integration. Merely editing both files is not acceptance.

Financial: handle the stated domain and edge cases exactly, retain focused tests,
and obtain an actual separate read-only correctness review. Identify the reviewer
in native lineage and inspect its findings and their disposition. Parent rereading
cannot stand in for the task's explicit independent review requirement.

Resume: preserve the existing dirty note byte for byte, correct the live behavior,
and run a relevant current check. Prior success text is insufficient evidence.

UI: operate the provided session using normal input, confirm visible selected
theme and persistence after reload, capture and inspect the final screenshot,
and report the actual result. Source substrings or PNG presence alone cannot pass.

## Adjudication

If evidence is ambiguous, record unknown or a specific unmet criterion. Do not
infer a command ran from a final answer saying it did. Record disagreements and
resolve them against artifacts under this rubric, retaining both judgments.
Deterministic grader defects require a new version and fresh matched runs; they
cannot be repaired by overriding the inconvenient assertion in the audit sidecar.
