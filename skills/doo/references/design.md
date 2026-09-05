# Design and grill

Use this reference for doo plan, explicit doo grill, or an ordinary task whose design is consequential. Keep the design proportional to the unresolved risk.

## Ordinary design

Read the existing code and repository terms before proposing a shape. Identify the data that crosses the important seam, the state transitions that matter, the callers, and the acceptance checks. Reuse an existing interface and dependency when it already expresses the behavior. Prefer a small interface with behavior behind it and a test surface that follows the same seam.

Use a prototype only when an observable experiment can settle a consequential unresolved question, such as a state model, interaction, or competing interface. Keep it throwaway, easy to run, visibly marked, and free of production persistence by default. Fold only the validated decision into the real implementation and record the question and verdict.

An ordinary design can proceed when the criteria are concrete and no user preference remains unresolved. It does not require a panel, a full interview, a glossary, or an ADR for every change.

## Explicit grill mode

doo grill is a design interview, not an implementation shortcut. Build a dependency tree of every decision needed for the requested design. A decision is a node. Its prerequisites are the nodes it depends on. The frontier is the set of currently unblocked nodes.

Work in rounds:

1. Inspect the repository, current terminology, relevant code, tests, and other observable sources. Resolve factual questions yourself.
2. Recompute the frontier from the facts and the user's prior answers.
3. Ask every question on that frontier in one round. Number each question, explain the decision it controls, and give a recommendation with its reason. A question that depends on an unanswered question waits for a later round.
4. Record the user's answers, update the tree, and continue until no decision remains silently assumed.

Use this shape for a question:

    Q1. Decision title
    What choice is needed, what depends on it, and what concrete scenario distinguishes the options?
    Recommended answer. State the choice and the evidence or trade-off behind it.

Investigate facts with the available filesystem, source, tests, running application, or other authorized tools. Ask the user only for a product, policy, or preference decision that the environment cannot settle. Do not use a user-facing question to hide missing research.

Apply domain modeling throughout the interview:

- Reuse existing canonical terms. If a term is overloaded or conflicts with repository language, name the ambiguity and propose a precise term.
- Stress-test relationships with concrete scenarios, including boundary and failure cases.
- When a term is resolved, update the repository's existing glossary or context document in the format it already uses. Create a glossary only when terminology genuinely matters and the repository has no convention to follow.
- Offer an ADR only when the choice is hard to reverse, surprising without context, and the result of a real trade-off. Put it in the repository's established ADR location and format.

The interview ends only when the frontier is empty and the user confirms the shared understanding. That confirmation authorizes the design handoff, not unrelated implementation or release actions. Implementation requires an explicit instruction to proceed after the design. If the user asks to implement during an unfinished grill, record the remaining decisions and ask the current frontier first.

## Design output

Return the chosen model, rejected alternatives when they explain a trade-off, canonical terms, state transitions, interface and ownership boundaries, acceptance checks, and unresolved questions. Link any glossary, ADR, prototype verdict, or evidence created during the session. Never present an unconfirmed design as an implemented or verified result.
