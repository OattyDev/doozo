# Debugging

Apply reproduction, failure tracing, disproof, and consistent evidence. Scale the investigation to the uncertainty; no opening recital or fixed number of hypotheses is required.

## Reproduce and trace

Establish an observable failure before proposing a fix: exact input, runnable steps, and expected versus actual behavior. Use an existing test, request, CLI invocation, or small probe. For a flaky trigger, control the relevant timing, seed, or inputs until the signal can distinguish failure from success.

Trace where the real path diverges, including relevant callers and state. Choose source tracing, a debugger, or narrow instrumentation according to what will answer the question. Remove temporary probes after use.

When the supplied evidence cannot reproduce the incident, continue authorized investigation and identify the missing input or access. An unrelated failing example does not establish this incident's cause. A speculative patch is an unverified hypothesis, offered only if requested.

## Test the explanation

For an obvious local defect, one candidate cause is enough if a focused experiment can disprove it and nearby cases check the boundary. For ambiguous, intermittent, or interacting failures, rank the plausible alternatives and choose a discriminating experiment. Add hypotheses when observations demand them; do not invent alternatives to meet a count.

Change one relevant variable at a time. Reconcile each observation with the earlier evidence. If an explanation contradicts a previous run, resolve the contradiction before accepting it.

## Fix and verify

Fix the established cause, rerun the reproduction, and check relevant nearby behavior. A test should fail for the original defect and pass for the fix. Keep a brief input/observation/conclusion record for a short investigation; use an experiment ledger only when multiple attempts, flaky signals, or handoffs make it useful.

Report the cause, change, current checks, and remaining uncertainty. Apply the entrypoint's completion gate; a patch without an observed reproduction and post-fix check is not a verified incident fix.
