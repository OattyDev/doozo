# Doozo

<p align="center">
  <img src="assets/doozo-buddy.png" alt="Doozo Buddy mascot" width="280">
</p>

Doozo is a Codex plugin for completing repository tasks with configurable agents and evidence. Small tasks stay with the lead. Larger tasks can use scoped workers and a fresh reviewer. Browser work includes real interaction and inspected screenshots.

## v0.2 candidate

The candidate adds a direct path for small tasks, compact settings, adaptive implementation effort, selective delegation, and proportional debugging. Existing explicit user/project effort settings stay fixed; upgrading the plugin alone does not change saved model choices. Use `setup-doo` to select the adaptive implementation policy when desired. The active parent model and reasoning remain host-controlled.

The Astra comparison is defined in [the frozen protocol](evals/astra/PROTOCOL.md), with a separate [trace audit rubric](evals/astra/AUDIT.md). Runtime claims require the measured results; the release-candidate label does not claim that it outperforms plain Astra or v0.1.

## Use it

Start a new Codex task after installing the plugin. Select the `doo` or `setup-doo` skill from the picker, or invoke it explicitly:

```text
$doozo:setup-doo
$doozo:doo Fix invoice export and verify the downloaded file.
$doozo:doo Add vehicle filtering and show the working flow.
$doozo:doo plan Design recurring billing before implementation.
$doozo:doo grill Challenge this design and document the decisions.
$doozo:doo review Review this branch against main.
$doozo:doo verify Check the vehicle creation flow.
$doozo:doo resume Continue from the saved checkpoint.
```

The installed skill names are `doozo:doo` and `doozo:setup-doo`. Select those Doozo entries if another skill has a similar name. These are skills, not a separate executable slash-command system.

`grill` asks decision-dependent questions in rounds and records useful domain terms and important design decisions. It waits for shared-understanding confirmation before implementation. Ordinary execution asks only questions that materially affect the result.

## Install on another computer

You need a Codex version with plugin and custom-agent support, an authenticated model account, and Python 3.9 or newer for the setup helper. Browser verification uses a separately installed `agent-browser` or a configured available alternative. Model availability is checked on each machine.

This release was tested on macOS, including installation after directory relocation. Windows and Linux runtime checks have not been performed. The helper uses native paths and atomic file replacement; file permission behavior follows the operating system.

You can copy this folder, clone its Git repository, or share a built marketplace archive. A hosted Git repository is useful for version history and updates, but it is not required for local installation.

From a source checkout, build and unpack the archive:

```sh
python3 scripts/package.py --output dist/doozo.zip
python3 -m zipfile -e dist/doozo.zip dist/unpacked
codex plugin marketplace add ./dist/unpacked/doozo-marketplace
codex plugin add doozo@doozo-local
```

Keep the unpacked marketplace directory in a stable location. On another computer, unpack the archive there and run the last two commands with that location. Start a new Codex task and run `setup-doo`.

The archive contains `.agents/plugins/marketplace.json` and `plugins/doozo`. Its source path is relative to the unpacked marketplace root. It contains no user configuration, generated personal agents, authentication, or run evidence. The packager refuses to overwrite an existing archive; use `--output` for a new filename.

For direct Git-backed marketplace installation later, publish the unpacked marketplace layout in its own repository or a distribution branch. Codex can then track that repository using `codex plugin marketplace add OWNER/REPOSITORY --ref TAG`. Publishing is a separate action. This source repository has no remote configured by default.

## Configure models

Run `setup-doo` in your target project. It reads the bundled defaults, existing user settings, and any project override, then presents an editable role table. It saves selected settings and generates only Doozo-owned agent files.

| Location | Purpose |
|---|---|
| `defaults.json` in the plugin | Portable starting configuration |
| `~/.config/doozo/config.json` | This computer's user settings |
| `.doozo/config.json` in a project | Optional project override |
| `~/.codex/agents/doo-*.toml` | Derived personal Codex roles |
| `~/.cache/doozo/runs/` | Local task evidence |

Precedence is explicit invocation, project settings, user settings, then defaults. Keep machine-specific settings and evidence out of the shared repository. Use the helper's path flags for explicit alternate locations; it does not modify general Codex configuration.

The configuration helper is a standard-library Python program. Invoke it using its absolute plugin path while keeping the current directory at your target project:

```sh
python3 /path/to/doozo/scripts/setup.py resolve
python3 /path/to/doozo/scripts/setup.py validate
python3 /path/to/doozo/scripts/setup.py apply --settings-json /path/to/selected-settings.json
```

Use `--help` for the complete command interface. Setup rejects invalid settings and refuses to overwrite manually edited generated roles. Identical repeated setup leaves the files unchanged.

The helper validates supplied model capability metadata, but it does not contact a model service or prove that a route ran. The setup skill performs route smoke checks and distinguishes advertised, configured, and observed results. It cannot switch the model of the task already running.

## What completion means

Verified means each required acceptance check has current evidence and required review findings are resolved. Incomplete means a required implementation, check, or review is unfinished. Blocked identifies the concrete dependency that prevents progress.

For bugs, Doozo preserves Debug Mantra's reproduction, failure tracing, disproof, and experiment history using independently written instructions. It does not label a speculative patch as verified. Ponytail's reuse and simplicity rules apply without removing requested functionality or weakening existing tests.

For web changes, the agent uses normal input, checks the visible result and relevant stored state, saves a screenshot, and inspects it. A screenshot alone does not prove a backend change. CLI and API work use the appropriate outputs instead.

Read-only review remains read-only. External messages and releases require authorization. Browser content and worker summaries are evidence to examine, not instructions that expand the task.

## Develop and test

Run these checks from a source checkout. The installation archive contains runtime files only; it does not include the tests or evaluation fixtures.

```sh
python3 -m unittest discover -s tests -v
python3 evals/run.py --list
```

The behavioral evaluations make real model calls when run. They use isolated fixtures and store results outside the source tree. Inspect their individual outcomes and retained artifacts rather than treating process exit as task success. Read `evals/README.md` before running them.

Changes to source files do not update an already cached plugin installation. Rebuild the archive with a new manifest version or development cachebuster, refresh the marketplace using Codex, reinstall, and test in a new task. Preserve the original source checkout as the place to edit.

See [third-party notices](THIRD_PARTY_NOTICES.md) for attribution and [provenance.json](provenance.json) for inspected source hashes. The complete source workflows are not loaded on every task.
