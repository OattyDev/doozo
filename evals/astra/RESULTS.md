# Doozo v0.2 candidate: Astra benchmark

**Do not promote this candidate as a proven performance improvement.** It preserves
useful workflow safeguards and reduces some v0.1 overhead, but misses the frozen
10% token-reduction target. Plain Astra completed the same tasks with fewer total
tokens. Connection failures and large host timing gaps also prevent a clean
full-matrix timing conclusion.

The implementation is `0.2.0-rc.1` on `codex/doozo-v0.2`. During final verification,
the local marketplace had refreshed its cache from the editable candidate source.
The candidate was isolated in an unregistered worktree and stable v0.1 restored.
Personal model settings remain unchanged. No “AGI skill” claim is made.

## What changed

Five bounded changes were saved separately, after the original benchmark freeze:

| Stage | Change | Source commit |
|---|---|---|
| S1 | Small, low-risk tasks skip the full execution reference, planning, delegation, and ledger | `a1d2ad9` |
| S2 | Entry point owns routing/review/completion rules; references carry conditional detail; compact settings omit duplicate configuration | `38712fe` |
| S3 | Implementation effort resolves from an adaptive policy to a concrete supported worker route | `6bb3c72` |
| S4 | Delegate independent work only when it earns its cost; parent retains integration and final acceptance | `e038a9b` |
| S5 | Keep reproduction, tracing, disproof, and consistent evidence without a recital or fixed hypothesis count | `2fe8d17` |

Independent source review restored the existing high-consequence review catch-all
and preset route preferences in `50ebba3`. The corrected staged snapshots include
that same correction from S2 onward. Branding and packaging behavior were preserved.

`setup.py resolve --compact --task-complexity bounded|complex` resolves adaptive
implementation roles to `medium` or `high`. The helper owns that mapping. Existing
explicit user/project/invocation efforts remain fixed; no saved `max` choice is
silently changed. The active parent model and reasoning remain host-controlled.

## Primary comparison

The [protocol](PROTOCOL.md), [audit rubric](AUDIT.md), and [freeze manifest](FREEZE.json)
define the comparison. The original freeze was commit `c107251`, before S1. The
current corrected grader freeze is protocol 3 at `176dd83`.

All three arms used Astra at `medium`, the same app-bundled Codex CLI 0.153.0,
sequential isolated fixtures, a two-worker cap, common host skills, and rotated
arm order. The installed Doozo was disabled in every arm; Doozo arms loaded their
explicit frozen snapshot. Project settings isolated the compared profiles from
personal overrides. Plain Astra could choose its normal route from the common
available model roster. Its financial reviewer used Astra; Doozo used configured
Sol/high reviewers. These route choices are part of the compared workflows.

There were eight task types, two repetitions, and three arms: **48 initial task
runs**. First-pass means completion during that initial unassisted task run.
Internal failed tool/check attempts remain retries in the table; a later complete
task rerun never replaces a failed first pass.

| Measure | Plain Astra | Astra + v0.1 | Astra + v0.2 candidate |
|---|---:|---:|---:|
| Successful initial task runs | 16/16 | 15/16 | 16/16 |
| Total tokens, parent plus descendants | 2,782,046 | Unknown; observed lower bound 3,253,854 | 3,597,639 |
| Internal retries | 7 | 2 | 7 |
| Whole-task reruns within this matrix | 0 | 0 | 0 |
| Actual human interventions | 0 | 0 | 0 |
| Requests for missing incident evidence | 2 | 2 | 2 |
| Unnecessary tool/test invocations | 7 | 8 | 9 |
| Test-runner invocations | 18 | 16 | 22 |
| Code regressions found | 0 | 0 | 0 |
| Missed criteria | 0 | 5 in the timed-out attempt | 0 |
| Recorded active-time sum, not comparable wall time | 1,051.417 s | 1,840.958 s | 1,703.102 s |

The v0.1 failure was a 600-second timeout with WebSocket disconnects before an
implementation change. It is retained as an operational first-pass failure,
**not evidence that v0.1 caused a code regression**. Its final usage is unknown;
72,473 observed tokens from that attempt are only a lower bound.

Two plain-Astra financial totals were independently recovered from native actor
records: 502,635 and 427,941 tokens. Full-history forks copied a parent's active
turn marker into the child log, causing the frozen collector to return unknown.
The child-local final counters, own completed turns, and native parent links prove
the totals under the unchanged counting equation. Original null values remain in
raw results; supplemental accounting records are separate. Cached input and
reasoning output are subsets, not additional tokens.

The [48-row data file](results-primary.json) retains every primary outcome,
recorded duration, retry count, limitation, and evidence hash. Raw traces, original
results, screenshots, and audit sidecars remain local; no authenticated session
logs were published.

## Before/after evidence

For the 15 mutually correct and timing-comparable v0.1/v0.2 pairs, the median of
per-pair candidate/baseline ratios is:

- **Tokens: 0.9361 — 6.4% lower**, short of the required 10% reduction.
- **Recorded active time: 0.8813 — 11.9% lower**, a descriptive subset result.

This subset excludes the failed/disrupted financial repetition. It does not
rescue the full-matrix acceptance gate. The three arms' financial repetition 2
had large wall-clock versus active-clock discrepancies. Plain's 169.559 active
seconds spanned about 4,082 wall seconds; the candidate's 530.795 active seconds
spanned about 6,205 wall seconds. The v0.1 run timed out without terminal completion.
A temporary idle-sleep inhibitor was used for later collection, which cannot
retroactively make those measurements comparable.

The candidate used **29.3% more total tokens than plain Astra** and produced the
same 16/16 initial-run task success. Internal repairs occurred in both workflows;
this is not a claim that either was error-free on its first tool invocation.

The following task medians show where the tradeoffs occur. Each cell is
**thousands of total tokens / active seconds**. Ordinary rows use two repetitions;
the financial row uses only the first, comparable repetition and is marked `n=1`.
The second financial repetition remains in the full outcome table and data file.

| Task | Plain | v0.1 | v0.2 |
|---|---:|---:|---:|
| Exact document correction | 65.9 / 24.9 | 124.5 / 44.4 | 104.9 / 40.9 |
| Whitespace bug | 120.4 / 51.4 | 211.3 / 81.0 | 146.1 / 50.5 |
| Missing incident reproduction | 128.0 / 48.7 | 155.9 / 82.1 | 135.5 / 60.0 |
| Bounded standard-library feature | 89.6 / 40.6 | 122.9 / 50.6 | 117.5 / 46.7 |
| Multi-module feature | 93.5 / 61.6 | 155.7 / 66.9 | 135.5 / 77.0 |
| Financial correction + review, n=1 | 502.6 / 145.1 | 716.4 / 205.3 | 807.4 / 281.6 |
| Resume with dirty file and stale evidence | 133.6 / 55.9 | 142.4 / 76.3 | 138.0 / 65.7 |
| Browser toggling and reload persistence | 294.8 / 85.4 | 319.9 / 116.6 | 275.3 / 104.4 |

Plain Astra was cheaper on seven of these eight task rows. It was faster on seven;
the candidate's whitespace median was only about one second faster. The candidate
used fewer tokens for the browser fixture but took longer. It was slower than
v0.1 on both multi-module repetitions despite using fewer tokens.

## Verification and remaining waste

Independent audits checked actual source, tests, command traces, separate reviewer
identities, and all six final browser screenshots. Both themes and reload persistence
worked; the task actors also inspected their screenshots. All dirty user files and
supplied tests were preserved. Missing-reproduction cases named missing evidence
without inventing an incident fix.

The shorter debugging flow preserved reproduction and regression checks. Neither
candidate whitespace attempt used a recital or fixed hypothesis count. The v0.1
attempts did. The primary multi-module attempts all stayed local, so they do not
measure implementation-worker effort or a change in delegation behavior.

The financial reviews exposed real overhead: failed shell commands, an empty test
discovery run, a cache-writing syntax check after imports had already succeeded,
and repeated passing checks. Each browser attempt also retried a relative
screenshot path with an absolute path. Those failures remain in the retry and
waste counts. A valid `rg` search with no matches was correctly excluded from
waste after an independent audit correction; both audit versions are retained.

## Staged diagnostics

Ten separately identified adjacent-stage runs test attribution. They are excluded
from the primary denominator and cannot establish statistical causality with one
pair per change. All ten task outcomes were independently audited. Values below are one run per
side, not averages or additional primary repetitions.

| Probe | Tokens before → after | Seconds before → after | What the evidence supports |
|---|---:|---:|---|
| S1 fast path | 124,413 → 93,326 | 44.472 → 32.637 | Direct path was exercised; both document outcomes correct |
| S2 deduplication/compact settings | 184,200 → 150,505 | 65.150 → 55.348 | Less startup context on resume; dirty work preserved |
| S3 adaptive implementation effort | 636,022* → 518,858 | 137.537 → 112.936 | Actual Luna/max → Luna/medium worker routes, parent integration retained |
| S4 selective delegation | 117,744 → 117,504 | 53.015 → 45.631 | **Not exercised:** both attempts stayed local; no delegation benefit can be attributed |
| S5 proportional debugging | 203,674 → 146,295 | 83.807 → 87.990 | Reproduction/disproof preserved; fewer tokens but a slower run |

The S3 baseline's automated status remains a failure with null total because the
collector mixed inherited parent route metadata with the child's actual route.
Independent native-record accounting proves its actual Luna/max worker used
290,312 tokens and its parent used 345,710, totaling **636,022**. This is separate
supplemental evidence, not a successful replacement run or an edited raw result.
Both code outcomes were correct, but their original automated fields are not
directly comparable without that accounting caveat.

The S3 candidate's first post-edit check failed on an unquoted zsh glob. It was
corrected within the initial run; its audit retains the failed check, one retry,
and five unnecessary executions. The baseline had three unnecessary executions.
These diagnostics identify promising components and unexercised behavior; they
do not override the primary acceptance decision. See [diagnostic data](results-diagnostics.json).

## Integrity and decision

Eight earlier started document attempts are retained outside the primary matrix.
Protocol 1 incorrectly rejected an authorized evidence artifact. Protocol 2 still
imposed an evidence directory that the task had not specified. Independent review
confirmed both conflicts. Protocol 3 protects the supplied files and requested
text, leaving the legitimacy of added evidence to semantic audit. Entire affected
blocks were restarted; no original failure was rewritten as a success.

These are small synthetic tasks in this user's populated Codex environment, not
production migrations or a clean-room model evaluation. Timing variation,
transport failures, host suspension-like gaps, and limited repetitions constrain
what can be concluded. Historical Luna samples do not enter any acceptance gate.

The candidate fails the frozen token-improvement threshold, does not reduce waste
relative to v0.1, and lacks a clean full-matrix timing comparison. Keep it as a
reviewable candidate. Plain Astra is the stronger default for the well-specified
small tasks demonstrated here. Further changes should target observed tool-path
and review overhead in separate measured changes, preserving the evidence and
verification requirements.
