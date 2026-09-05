# Execution

Use this reference for ordinary doo work. Its job is to carry a bounded request to an observable result without adding ceremony that the task does not need.

## Start with a contract

Use the effective settings resolved at skill startup. Read the user's request, repository guidance, and current working-tree changes before editing. State the requested outcome in concrete terms and list the checks that would demonstrate it. Identify files, services, data, accounts, and external systems inside the user's scope. Preserve unrelated changes.

Classify the request before choosing a route:

- A small local change can stay with the parent.
- Independent frontend, backend, documentation, or investigation scopes may use separate workers.
- A bug follows [debugging.md](debugging.md).
- A consequential design choice follows [design.md](design.md).
- A substantial or sensitive change may require [review.md](review.md).
- A user flow, API, CLI, download, or visual result follows [verification.md](verification.md).

Treat the configured preset as a routing preference, not a second model table. Adaptive matches worker count and review depth to scope and risk. Quality-first requests an independent review for every code change and uses the strongest user-selected routes without substituting a model. Budget-first keeps small tasks local and uses the configured lower-cost routes, escalating to the complex role only when new failure or ambiguity evidence justifies it. Every preset keeps the required acceptance checks.

If a missing product decision could change the result, ask one focused question after doing the independent investigation that does not depend on its answer. An environment fact is evidence to collect, not a question to delegate to the user.

## Trace before editing

Follow the actual entry point, callers, data shape, state transitions, side effects, and relevant tests. Read repository conventions and reuse existing modules and dependencies. Before adding an abstraction or dependency, check the codebase, standard library, and platform feature for an existing fit. Simplify without deleting requested behavior or weakening the repository's checks. Name the important state when branches or persistence make it easy to confuse. Choose the smallest design that satisfies the contract.

Treat explicit directions as scope:

- plan produces a design and acceptance checks, then waits for an instruction to implement.
- review examines the requested baseline or working tree and reports findings.
- verify exercises the named behavior and reports evidence.
- resume restores the saved checkpoint, rechecks live state, and continues from the next unfinished criterion.

## Delegate by ownership

The parent owns requirements, decisions, integration, and the final verification. Keep a small task local. When a worker earns its cost, give it exact paths or modules, permitted actions, acceptance criteria, dependencies, and required checks.

Use these roles when the host and effective settings expose them:

- scout maps source, tests, risks, and disjoint write scopes. It is read-only.
- implementer handles one bounded implementation scope.
- complex implementer handles a bounded difficult scope with its explicit dependencies.
- reviewer performs a fresh read-only correctness review.
- browser verifier exercises a live user flow and records evidence without editing application code.

Use each `route_status[role].agent_name` returned by setup as the exact custom agent type. These are `doo-scout`, `doo-implementer`, `doo-complex-implementer`, `doo-reviewer`, and `doo-browser`. Generic host types with similar names are not those configured roles. If the named type is unavailable, use a fresh explicit model-and-reasoning route only when the host supports it and preserves the role's instructions and permissions. Otherwise report the unavailable route. The orchestrator has no child agent type.

Keep workers disjoint. One owner handles each shared fixture, lockfile, generated output, migration, test account, and evidence directory. Repartition or serialize when scopes overlap. Do not create a child orchestrator. Respect the configured worker cap and occupied host slots.

Role selection is evidence, not a promise. Use the selected model and reasoning route from effective settings. If an invocation or project override differs from a generated role, use a supported fresh route that exposes the requested settings. Do not claim a role uses a different model because its prompt says so. Do not silently fall back when a model, reasoning value, or required tool is unavailable.

## Implement in checkable units

Make the smallest change that satisfies the accepted contract. Keep transient probes identifiable and remove them before completion. Run the focused checks after each meaningful unit. Reuse the repository's test runner and fixtures. Add regression coverage when it materially detects the requested behavior; do not invent a test quota or a parallel test system.

For a bug, a proposed fix waits for a reliable reproduction and a narrowed fail path. For a UI or other externally observable change, exercise the real path through its normal interface. For a data or API change, inspect the stored or returned result. See [verification.md](verification.md).

## Review and integrate

Request a fresh review when the change is substantial or touches authentication, authorization, financial calculations, concurrent state, data migrations, destructive operations, or other high consequence behavior. Give the reviewer the original requirements, baseline revision, actual diff, relevant source, and commands. Do not prime it with the implementer's conclusion.

The required reviewer must be a separate agent or reviewer as defined in [review.md](review.md). If that route is unavailable, report Incomplete. Re-reading the code yourself does not complete the independent review step.

Resolve accepted findings in the owning scope. Any change after review invalidates the affected review and evidence, so rerun the affected checks and obtain a new review when the risk still warrants it. The parent inspects the final diff, untracked files, command output, and user-facing artifact before claiming completion.

## Keep evidence proportional

Small API or CLI work can be proven with responses, exit codes, stored state, or output files. A substantial run keeps an evidence directory as described in [verification.md](verification.md). Record sanitized commands, working directories, timestamps, exit codes, concise outputs, baseline and final working-tree fingerprints, and artifact paths. Keep credentials and authentication state out of evidence.

Use the completion status that the evidence supports:

- **Verified** means every acceptance check is current and any required review is resolved.
- **Incomplete** means implementation exists but a required check, review, or step is unfinished.
- **Blocked** means a concrete external dependency prevents the next required step.

Report the behavior, files, checks and results, evidence paths, review disposition, and unresolved concern. Never turn an unobserved assumption into a verified claim.
