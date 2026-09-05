# Debugging

Use this reference when the user reports a bug, failure, exception, regression, or asks for diagnosis. Begin the first response of the debug session with this four-line reminder, once:

> Establish a reliable reproduction before changing code.
> Trace the real failing path, using a debugger before source tracing and probes where possible.
> Try to disprove ranked explanations before accepting one as the cause.
> Treat every run as evidence and reconcile it with the full experiment ledger.

This is an original portable wording of the four-step Debug Mantra discipline. Keep its order and evidence standard.

## 1. Reproduce

Build a runnable pass or fail signal before proposing a fix. Capture exact steps, inputs, environment, and the failure output in a test, script, request, CLI invocation, replay harness, or other artifact. For a flaky trigger, improve the signal with controlled repetition, narrowed timing, a fixed seed, or isolated inputs. Do not turn a patch into a verified fix when no reliable reproduction exists.

If the reproduction is missing, continue authorized evidence gathering and state what access or artifact is needed. A speculative patch may be offered as a hypothesis only when the user explicitly asks for one. It remains incomplete until the failure and its absence after the fix can be observed.

## 2. Trace the fail path

After reproduction, locate where the behavior diverges and what prevents it from diverging in nearby cases. Try these in order and escalate only when the earlier route cannot answer the question:

1. Attach a debugger and step to the failure when the environment supports it.
2. Trace the source path end to end and enumerate influencing knobs such as configuration, environment, flags, input shape, branch conditions, timing, concurrency, and build options. Change one axis at a time.
3. Add narrowly scoped instrumentation at the suspected divergence. Give every probe a unique marker so it can be found and removed. Record the relevant state, then clean the probes before completion.

## 3. Falsify hypotheses

List three to five ranked explanations before committing to one. Walk each explanation through the full symptom. Identify the simplest disproof and run it first. A surviving explanation still needs a positive experiment that distinguishes it from its nearest alternative.

Do not use an arbitrary reproduction speed, flake percentage, or number of bug findings as a universal pass threshold. Use the signal that makes this failure distinguishable and repeatable in this environment.

## 4. Keep the ledger

After every run, record the input or change, the observation, and what it ruled in or out. Cross-reference new explanations against every earlier breadcrumb. A hypothesis that contradicts a prior run is wrong or incomplete until the contradiction is explained.

The final debug record names the reproduction, fail path, disproof attempt, accepted cause, fix, regression check, and any missing evidence. If a review or later change invalidates the checks, rerun the affected experiments before claiming the bug is fixed.
