# Doozo v0.2 Astra comparison — protocol 2

Defined before changing the plugin implementation. Historical Luna runs are
baseline observations only; neither their selected reruns nor their timings
decide whether v0.2 improves Astra.

Protocol 2 corrects one independently confirmed doc-grader defect: the common
prompt permits fixture evidence, but protocol 1 rejected the added evidence file.
Allow new evidence files under `evidence/`, whether committed or untracked; retain
the exact requested document and reject changes to other supplied files. Keep
all six started protocol-1 doc attempts and their original grading untouched.
The affected matched block is invalidated by a separate record and rerun in full.
No other task grader, acceptance gate, or measurement formula changes. Source
review also restored existing review/preset rules in candidate revision 2 before
the replacement matrix; its snapshot hash distinguishes it from revision 1.

## Question and arms

Does the focused v0.2 workflow preserve correctness while reducing total model
work and elapsed time in this user's Codex environment?

- **plain:** Astra with the common host instructions, without Doozo invocation.
- **v01:** Astra with Doozo at commit `a1d09a2`.
- **v02:** Astra with the frozen candidate implementing priorities 1–5.

The parent is `gpt-6-astra`, requested effort `medium`, in every arm. Record the
actual model and effort from runtime metadata. Do not substitute another model.
The runtime pilot is excluded from task scores: PATH CLI 0.146.0 rejected Astra;
the app's bundled CLI 0.153.0 accepted it. Use the latter for every arm.

## Conditions

Use fresh Git fixtures and sessions, identical task text, initial files, tool
access, sandbox, deadlines, and host settings for each matched task. Disable the
installed Doozo plugin in every arm; explicitly supply only the selected frozen
skill snapshot to the two Doozo arms. Other installed skills remain common, so
"plain" means this host without Doozo, not an instruction-free model.

Use isolated project settings to prevent personal role choices from masking
the candidate's defaults. Preserve the same model roster and two-worker cap;
worker effort and delegation decisions are treatment variables. User overrides
are checked separately with deterministic configuration tests. No global user
settings or generated personal agents are rewritten for the experiment.

Run one top-level task at a time, with a 600-second deadline. Rotate arm order
by task and repetition. Run eight task types twice (48 initial attempts): doc
correction, simple whitespace bug, missing reproduction, a new bounded stdlib
feature, a feature spanning independent modules, sensitive financial rounding,
dirty resume with stale evidence, and a constrained UI change. The exact task
inputs and executable graders are frozen in `astra_tasks.py` before plugin edits.
Provision the same isolated browser resources for every UI arm; exclude host
browser startup and grader time from agent elapsed time, and record them separately.

This is a small local comparison. Report individual paired results and medians;
do not claim broad statistical superiority or infer billing from token counts.
Service load, shared prompt caches, and model nondeterminism remain limitations.
Record runtime version, snapshot hashes, host skill/config fingerprints where
observable, and start times. Drift in these conditions invalidates the affected
matched block rather than becoming evidence for either arm.

## Frozen grading and measurements

Graders run after the agent exits, outside its fixture. Check requested behavior
and hidden boundary cases, preservation of existing tests and unrelated work,
and any required browser outcome. Never grade by a particular patch spelling.
Retain raw events, final responses, diffs, artifacts, and grader results locally.

For every attempt record:

1. **First-pass correctness:** all behavioral requirements met in the initial
   unassisted task run, including honest reporting and any explicitly required
   review or evidence. A correct request for unavailable evidence is success
   on the missing-reproduction task; inventing a fix is failure.
2. **Total tokens:** cumulative input plus output across parent and every
   descendant exactly once. Input includes cached input; report the cached
   subset separately. Reasoning tokens are a subset of output, not an addition.
   Use each actor's final cumulative usage, not a sum of cumulative events.
   Missing lineage or usage makes the aggregate unknown, never zero.
3. **Elapsed time:** parent launch through completion, including worker waits.
4. **Retries:** report internal failed tool/verification attempts and external
   task reruns separately. Root turn failure or timeout remains in the dataset.
5. **Human interventions:** clarification, permission, or rescue requests and
   actual human replies. No ad hoc replies during timed runs; unresolved requests
   count as unmet requirements unless abstention is the task's expected result.
6. **Unnecessary tool/test executions:** independently inspect the trace for
   unchanged passing checks repeated without new evidence, unrelated broad
   checks, avoidable failed invocations, or duplicate investigations. Keep total
   tool/check counts separate. Additional relevant verification is not waste.
7. **Regressions/missed requirements:** enumerate failed assertions, changed
   protected files, omitted requested behavior, and unsupported completion claims.

Semantic trace judgments use a fixed rubric and a reviewer who was not the task
implementer. Hide arm labels when practical; skill content may reveal the arm,
so do not claim full blinding. Pending judgments remain pending. Do not replace
unknown metrics with inferred favorable values.

An attempt is one initial agent run. Its own test/fix cycle is allowed and counted;
a later fresh run or human follow-up is a separate retry with a linked attempt ID.
Never replace or delete the original row. No automatic successful-rerun selection.
If a grader defect is discovered, retain its original output, version the corrected
protocol/grader, and rerun the entire affected matched block. Do not tune graders
after seeing one arm fail so it passes retroactively.

## Acceptance and stopping rules

Require zero fabricated verification claims, unauthorized side effects, or lost
user changes. Candidate first-pass successes must be at least v01's and plain's
in aggregate, with no repeatable new task-category regression. Report every
discordant pair rather than hiding it in an average.

To recommend v02 as an efficiency improvement, require complete worker usage
and trace audits, at least 10% lower paired median total tokens and elapsed time
than v01 on mutually correct attempts, and no increase in human intervention or
external retry counts. Also report cost/time over ALL attempts so cheap failures
cannot improve the score. Compare plain separately and name where it wins.
For each mutually correct case/repetition, divide v02's measurement by v01's;
take the median of those paired ratios. Each efficiency gate requires a ratio
at most 0.90. Report the number of pairs, individual ratios, and full ranges.
These are local engineering gates, not statistical proof. A mixed or incomplete
result leaves v02 a candidate with limitations; do not announce a proven upgrade.

Stop paid runs for authentication/rate-limit failures, unobservable model identity,
broken fixture isolation, or pervasive infrastructure failure. Preserve started
attempts. Do not spend repeated calls on an unchanged environmental blocker.
Run missing blocks later under the same protocol or explicitly version conditions.

## Attribution without a broad rewrite

Save separate implementation commits/snapshots for: S1 fast path, S2 shared-rule
deduplication, S3 adaptive worker effort, S4 selective delegation, S5 proportional
debugging (final v02). Keep model roster, setup precedence, permissions, browser
contract, branding, and packaging behavior stable.

Run adjacent-stage comparisons on prespecified probes, one repetition each:
S1 versus v01 on doc correction; S2 versus S1 on dirty resume; S3 versus S2 on
the multi-module feature; S4 versus S3 on the bounded stdlib feature; S5 versus
S4 on the simple bug. These ten runs are diagnostic, excluded from the primary
48. If a task does not exercise its intended change (for example no delegation
for S3), record "not exercised" rather than crediting a saving. Interactions and
single-run noise prevent causal claims from these probes alone.

For the S3 diagnostic only, append the same request to both stage prompts:
"Delegate formatting.py and its new tests to one implementation worker; the
parent owns catalog.py and CLI integration." This isolates worker effort on a
real permitted scope. The primary multi-module task keeps delegation optional.

Freeze protocol, tasks, runner, and graders by SHA-256 before implementation.
Unit-check fixture outcomes and usage aggregation before that freeze. Changes
after freeze need a new protocol version and explicit invalidation as above.
