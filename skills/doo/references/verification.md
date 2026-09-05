# Verification and evidence

Verification answers the acceptance checks with current observations. A successful command is evidence for that command, not proof of an untested user outcome.

## Match the check to the surface

For API work, inspect the actual response, status, error behavior, persisted state, and authorization result. For CLI work, inspect exit status, output, files, and repeated or reload behavior when persistence matters. For a library, exercise the public interface and meaningful failure cases. Reuse the repository's existing tests and runners.

For a web or desktop user flow:

1. Use the effective `browser.preferred` driver. The default is agent-browser. For that driver, run `agent-browser skills get core` before browser work so the instructions match the installed version. Load dogfood for exploratory QA and only the specialized guide that matches the surface. For another selected driver, read its available instructions and confirm it can perform the required interaction.
2. Use normal clicks, typing, navigation, and other user actions. Do not replace the acceptance path with hidden state or an implementation shortcut.
3. Check the visible result and the underlying effect when relevant. Reload to prove a saved record survives. Inspect downloaded files rather than only the download event. Try the unauthorized path when permissions are part of the requirement.
4. Capture a meaningful final screenshot. Inspect the image itself. Record its path, tested URL or route, viewport, and the user-flow steps. For visual regression, retain comparable before and after images with viewport information. Use video when timing or a multi-step interaction adds evidence.
5. Inspect relevant console errors and failed network calls. A screenshot or automated scan alone does not establish a full accessibility audit.

Use an existing Playwright or project verification suite for durable regression coverage. If the preferred live driver is unavailable, use `browser.fallback` only when configured or when the user has explicitly authorized an alternative. Otherwise report the missing capability. Name the driver and the exact criterion it proved. Do not describe a fallback as equivalent without checking the same observable criterion. The separate interactive Playwright workflow is not assumed to be available in every Codex host.

## Evidence contract

For substantial work, create a unique run directory at ~/.cache/doozo/runs/<run-id>/ with user-only permissions. Keep these records:

- requested requirements and each observable acceptance check;
- baseline revision and final revision or working-tree fingerprint, including relevant untracked files;
- commands, working directories, timestamps, exit codes, and concise sanitized output;
- screenshot or artifact paths, URL and viewport when applicable, and tested user-flow steps;
- review findings, dispositions, and the state that was reviewed;
- remaining blockers, excluded scope, and the evidence that separates unrelated baseline failures from the change.

Keep synthetic data where possible. Never place authorization headers, cookies, passwords, token query parameters, signed URLs, or live authentication state in evidence. Inspect screenshots and output for sensitive data before retaining them. Local evidence is not automatically uploaded or shared. Retain it until the user requests cleanup or configures retention.

Give browser sessions, test data, processes, and evidence directories distinct owners. Cleanup removes only resources created for this run and preserves the evidence. A checkpoint for an interrupted task records the next unfinished criterion and the live resources it owns. On resume, recheck live state before reusing any evidence.

## Completion gate

Start the final check with the acceptance contract and direct inspection. Combine deterministic assertions with artifact inspection and independent review when the risk requires it. Do not claim that a screenshot proves persistence, that a passing unit test proves a browser flow, or that a model's self-description proves route identity.

Apply the completion statuses defined in [SKILL.md](../SKILL.md).

Coverage is the acceptance criteria. A correct run may find zero exploratory issues. Do not create an arbitrary bug quota or hide a missing check behind a changed label.
