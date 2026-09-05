# Execution

Use the acceptance criteria, settings, route selection, review triggers, and completion gate in [SKILL.md](../SKILL.md). This reference covers work beyond its fast path.

## Choose the work

Adaptive matches worker count and review depth to scope and risk. Quality-first requests independent review for every code change. Budget-first keeps small tasks local and escalates to the configured complex role when failure or ambiguity evidence warrants it. Presets change workflow preferences, not the model roster or acceptance criteria.

Follow the relevant entry point, callers, data shape, state transitions, and tests before editing. Reuse repository conventions, existing modules, standard-library and platform features. Choose the smallest design that satisfies the request without weakening existing checks. Resolve environment facts directly; ask about product decisions only when they materially change the result.

## Delegate by ownership

When a worker earns its cost, give it exact paths or modules, permitted actions, acceptance criteria, dependencies, and required checks. Available responsibilities are scout (read-only exploration), implementer (bounded changes), complex implementer (difficult isolated work), reviewer (read-only correctness), and browser verifier (live-flow evidence without application edits).

Use each `route_status[role].agent_name` from setup as the exact custom agent type. Generic host roles with similar names are different routes. If the named type is unavailable or its settings differ from the effective route, use a fresh explicit model-and-reasoning route only when supported and preserving that role's instructions and permissions. Otherwise report the unavailable route. The orchestrator has no child role.

Keep writes disjoint, including shared fixtures, lockfiles, generated outputs, migrations, test accounts, and evidence directories. Repartition or serialize overlapping scopes. Respect the configured worker cap and occupied host slots. Do not create a child orchestrator.

Use actual host route metadata as evidence. A model's self-description is insufficient. Do not silently substitute an unavailable model, reasoning value, or required tool; an unobservable identity remains configured but unconfirmed.

## Implement and integrate

Make checkable changes and remove transient probes. Reuse the repository's runner and fixtures. Add regression coverage when it materially detects the requested behavior. Run focused checks after meaningful changes; broaden them only for affected behavior or unresolved risk.

When review is required by the entrypoint, follow [review.md](review.md), including independent identity, evidence, accepted fixes, and affected re-review. Resolve findings in the owning scope. For user-facing or substantial evidence, use [verification.md](verification.md).

The parent inspects the final diff, untracked files, command results, and relevant artifact after integration. Worker summaries and prior passing checks do not establish the current final state.
