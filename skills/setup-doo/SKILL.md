---
name: setup-doo
description: Configure Doozo's role routes, models, reasoning, concurrency, browser preference, and fallback policy when the user explicitly asks to set up or change Doozo.
---

# Setup Doo

Use this skill only for an explicit setup or configuration request. Reading effective settings is allowed during doo execution; writing settings, generated agents, or project overrides requires the user's setup request.

## Inspect before changing

Read only the relevant Doozo settings and host capability metadata. Do not print credentials, cookies, tokens, or unrelated Codex configuration. Inspect existing generated Doozo agent files and the target write scope before proposing changes.

The canonical user settings file is ~/.config/doozo/config.json. A project override is .doozo/config.json when the user requests project scope. Effective precedence is defaults, then user settings, then project settings, then explicit invocation values, with deep merge at each layer. Read role names and bundled starting values from <doozo-plugin-root>/defaults.json so this skill cannot drift from the helper.

Present one editable table containing the orchestrator route, scout, implementer, complex implementer, reviewer, and browser verifier, plus reasoning values, preset, concurrency cap, browser preference, and the fallback policy values accepted by defaults.json. The orchestrator inherits the active task model and reasoning by default, but preserve an explicitly configured preferred orchestrator route and show it. The other routes use the bundled starting profile unless the user changes it. These are starting values, not proof that the host supports them. Offer only presets and fallback policies represented in defaults.json or the strict schema. Do not promise a fallback choice the helper cannot validate.

## Use the setup contract

Resolve the installed Doozo plugin root from this skill's location, keep the target project as the command working directory, and run the bundled script by absolute path:

    python3 <doozo-plugin-root>/scripts/setup.py resolve
    python3 <doozo-plugin-root>/scripts/setup.py validate
    python3 <doozo-plugin-root>/scripts/setup.py apply

The commands emit JSON. Common path overrides are --defaults PATH, --user-config PATH, --project-config PATH, and --agents-dir PATH. Resolve and validate accept --invocation-json JSON_OR_PATH for an ephemeral overlay. Apply rejects that option. Capability metadata can be supplied as --capabilities-json PATH or an accepted JSON value. The project config defaults to .doozo/config.json when it exists.

Resolve emits the effective deep-merged settings. Validate checks the effective settings against the strict schema and supplied capabilities, then emits validation JSON. Apply validates first, detects every generated-file collision before writing anything, atomically writes the selected canonical settings layer and derived Doozo roles, then emits JSON.

Apply accepts --settings-json JSON_OR_PATH and --write-scope user or project. Its default write scope is user. Personal apply derives agents only from defaults and user settings, ignoring project overrides. Project apply includes the project's settings and defaults to the target project's .codex/agents directory. Without settings, apply initializes a missing user layer from bundled defaults unless project scope was selected; otherwise it only regenerates derived role files. Per-task overrides are never persisted.

## Validate capability claims

Read the host's advertised models, supported reasoning values, available roles, concurrency limit, and browser tools when those values are exposed. Reject an explicitly unavailable model or reasoning combination with the exact host error. An unknown capability is allowed only as unconfirmed. Record confirmed false and not advertised support rather than treating unknown as supported.

Run a small no-write smoke invocation through each distinct selected route after saving. Check actual route metadata when the host exposes it. A model's self-description, an API catalog, or an executable on PATH is not route evidence. If identity cannot be observed, report the route as configured but unconfirmed. The current task cannot switch its own active model; report a mismatch and explain that a host-supported new task or session is required.

Use generated roles only for their declared responsibility. Scout and reviewer remain read-only. Browser verifier may write evidence but does not edit application code. The orchestrator has no derived TOML because it inherits the active task route. Do not rewrite shared personal agent files to simulate a per-task override.

## Preserve and report

Derived personal agents belong under ~/.codex/agents/doo-*.toml unless the user explicitly selected project scope. Detect manually changed generated files and resolve the conflict before overwriting them. Preserve unrelated settings and agents. Each changed owned output retains one previous version in a .bak file. Setup preflights targets and backups, then replaces individual files atomically. This is not a transaction across all files; rerun after an interrupted apply to converge, or restore the appropriate backup.

Run resolve and validate again after apply. A second identical setup should produce no configuration changes. Report the effective values, selected write scope, generated paths, observed route metadata, unconfirmed capabilities, and whether a new session is needed. Do not claim setup confirmed a route that was only configured.

## Explicit-only task invocation

If the user asks to make doo explicit-only, this is a plugin invocation-policy change rather than a role setting. In the user's editable local plugin source, set `policy.allow_implicit_invocation` to false in `skills/doo/agents/openai.yaml`, preserving the other metadata. Use the host's supported local plugin update and reinstall flow, then verify the policy in a new session. Set it to true to restore automatic discovery when requested. Do not put this field in config.json or edit a shared installation cache. If no editable source is available, explain that a personal source copy and reinstallation are needed. Keep setup-doo itself explicit-only.
