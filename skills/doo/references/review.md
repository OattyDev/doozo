# Review

Use this reference for doo review or for an independent correctness check requested by ordinary execution. Review the actual result cold. The diff is the entry point, not the whole execution path.

## Pin the review

Resolve the requested baseline before reading findings. Capture the exact comparison, commit list, working-tree status, relevant untracked files, originating requirement, and repository standards. A missing or empty baseline is a review blocker until the scope is clear.

If the request supplies a spec, issue, acceptance list, or user-flow description, review against it. If no spec exists, say that the spec axis is unavailable rather than inventing one.

## Review two axes

Keep correctness and simplicity separate:

1. **Correctness and regression.** Trace each claimed behavior from entry point through callers, branches, state mutations, side effects, and exit. Inspect error paths, retries, partial failures, permissions, concurrency, persistence, and input boundaries. Check whether tests exercise that path or merely assert a mock or intermediate state.
2. **Simplicity.** Ask whether the requested outcome can be achieved by an existing module, dependency, platform feature, or smaller change. Look for unnecessary dependencies, dead abstractions, duplicated implementations, speculative generality, pass-through wrappers, and scattered changes. Treat simplicity observations as judgment calls and keep them separate from correctness findings.

For standards, use the repository's documented conventions first. For the spec axis, identify missing behavior, unrequested scope, and behavior that looks implemented but does not satisfy the requirement. Do not let a style observation hide a functional or security issue.

## Finding format

Order findings by severity. Each finding contains:

- **Finding.** One specific problem with a file and line or a precise path.
- **Why it matters.** The user or maintainer consequence.
- **Evidence.** The trace step, input, test result, or artifact that exposed it.
- **Suggested change.** The smallest change that resolves the problem.

If no issue is found, name the code paths, states, and checks inspected. A bare approval is not evidence. Do not invent a target number of findings.

## Freshness and disposition

An independent review comes from a separate agent or reviewer, not a second reading by the implementing parent. Record the reviewer agent or session identity, requested model and reasoning, actual route evidence where exposed, and returned findings. If a required independent route cannot run, keep the work Incomplete and name that blocker. Parent self-checks can supplement review but cannot satisfy this requirement or be relabeled as a fresh review.

Keep the reviewer read-only and do not prime it with the implementer's conclusion. Give it the original requirements, baseline, actual diff, relevant unchanged source, and commands. A reviewer finding is a claim until the parent reproduces it against the current tree.

Resolve accepted findings in the owning scope. Any change after review invalidates the affected review and evidence. Rerun the relevant checks and repeat the review when the changed risk still requires independent review. The parent owns the final disposition and must inspect the final artifact before reporting Verified.
