from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Optional
import unittest


PLUGIN_DIR = Path(__file__).resolve().parents[1]
SETUP = PLUGIN_DIR / "scripts" / "setup.py"


class SetupCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.user_config = self.root / "separate-home" / "config" / "doozo.json"
        self.project_config = self.root / "project" / ".doozo" / "config.json"
        self.agents_dir = self.root / "separate-home" / "codex" / "agents"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_json(self, path: Path, value: object) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def run_cli(
        self,
        command: str,
        *arguments: str,
        expect: int = 0,
        cwd: Optional[Path] = None,
        use_default_agents: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        command_line = [
            sys.executable,
            str(SETUP),
            command,
            "--user-config",
            str(self.user_config),
            "--project-config",
            str(self.project_config),
        ]
        if not use_default_agents:
            command_line.extend(("--agents-dir", str(self.agents_dir)))
        command_line.extend(arguments)
        result = subprocess.run(
            command_line,
            cwd=cwd or PLUGIN_DIR,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, expect, msg=result.stderr)
        return result

    def output(self, command: str, *arguments: str, **kwargs: object) -> dict[str, object]:
        return json.loads(self.run_cli(command, *arguments, **kwargs).stdout)

    def test_resolved_routes_identify_generated_agents(self) -> None:
        output = self.output("apply")
        self.assertIsNone(output["route_status"]["orchestrator"]["agent_name"])
        names = set()
        for role, route in output["route_status"].items():
            if role == "orchestrator":
                continue
            name = route["agent_name"]
            path = self.agents_dir / f"{name}.toml"
            self.assertTrue(path.is_file(), f"Route {role} has no loadable agent file")
            self.assertIn(f'name = "{name}"', path.read_text())
            names.add(name)
        self.assertEqual(len(names), 5)

    def test_compact_resolution_preserves_execution_settings(self) -> None:
        full = self.output("resolve")
        compact = self.output("resolve", "--compact")
        for key in ("preset", "max_workers", "model_fallback", "browser"):
            self.assertEqual(compact[key], full["effective"][key])
        for role, route in compact["route_status"].items():
            for key, value in route.items():
                self.assertEqual(value, full["route_status"][role][key])
        self.assertLess(len(json.dumps(compact)), len(json.dumps(full)))

    def test_parent_directory_alias_cannot_overwrite_config_with_agent(self) -> None:
        self.agents_dir.mkdir(parents=True)
        alias = self.root / "alias"
        alias.symlink_to(self.agents_dir, target_is_directory=True)
        self.run_cli("apply", "--user-config", str(alias / "doo-scout.toml"), expect=2)
        self.assertEqual(list(self.agents_dir.iterdir()), [])

    def test_partial_overrides_and_explicit_browser_fallback(self) -> None:
        self.write_json(
            self.user_config,
            {
                "max_workers": 1,
                "roles": {"scout": {"model": "custom-scout"}},
            },
        )
        self.write_json(
            self.project_config,
            {
                "browser": {"fallback": "cua"},
                "roles": {"scout": {"reasoning_effort": "high"}},
            },
        )
        invocation = self.root / "invocation.json"
        self.write_json(
            invocation,
            {
                "browser": {"preferred": "playwright"},
                "roles": {"reviewer": {"reasoning_effort": "medium"}},
            },
        )

        output = self.output("resolve", "--invocation-json", str(invocation))
        effective = output["effective"]
        self.assertEqual(effective["max_workers"], 1)
        self.assertEqual(effective["roles"]["scout"], {"model": "custom-scout", "reasoning_effort": "high"})
        self.assertEqual(effective["roles"]["reviewer"]["reasoning_effort"], "medium")
        self.assertEqual(effective["browser"], {"preferred": "playwright", "fallback": "cua"})
        self.assertEqual(output["route_status"]["scout"]["status"], "unknown")
        self.assertFalse(output["route_status"]["scout"]["advertised"])
        self.assertFalse(output["route_status"]["scout"]["confirmed"])

    def test_invalid_unknown_keys_and_boolean_worker_counts_are_rejected(self) -> None:
        for config, expected_message in (
            ({"max_workers": True}, "max_workers must be an integer"),
            ({"unexpected": "value"}, "unknown key"),
        ):
            with self.subTest(config=config):
                self.write_json(self.user_config, config)
                result = self.run_cli("validate", expect=2)
                self.assertIn(expected_message, result.stderr)
                self.user_config.unlink()

    def test_app_server_capabilities_advertise_but_do_not_confirm_routes(self) -> None:
        models = {
            "gpt-5.6-terra": ["medium", "max"],
            "gpt-5.6-luna": ["max"],
            "gpt-5.6-sol": ["high"],
        }
        capabilities = self.root / "models.json"
        self.write_json(
            capabilities,
            {
                "data": [
                    {
                        "model": model,
                        "supportedReasoningEfforts": [
                            {"reasoningEffort": effort} for effort in efforts
                        ],
                    }
                    for model, efforts in models.items()
                ]
            },
        )

        output = self.output("validate", "--capabilities-json", str(capabilities))
        self.assertEqual(output["capabilities_source"], "app-server")
        self.assertEqual(output["route_status"]["scout"]["status"], "advertised")
        self.assertTrue(output["route_status"]["scout"]["advertised"])
        self.assertFalse(output["route_status"]["scout"]["confirmed"])

        self.write_json(
            self.project_config,
            {"roles": {"scout": {"reasoning_effort": "ultra"}}},
        )
        result = self.run_cli("validate", "--capabilities-json", str(capabilities), expect=2)
        self.assertIn("is not advertised for model", result.stderr)

    def test_apply_is_idempotent_and_uses_injected_paths(self) -> None:
        unrelated_agent = self.agents_dir / "reviewer.toml"
        unrelated_agent.parent.mkdir(parents=True)
        unrelated_agent.write_text("keep this unrelated role\n", encoding="utf-8")
        first = self.output("apply")
        expected_paths = {self.user_config, *(self.agents_dir / f"doo-{role}.toml" for role in (
            "scout", "implementer", "complex-implementer", "reviewer", "browser"
        ))}
        self.assertEqual({Path(path) for path in first["written"]}, expected_paths)
        self.assertTrue(self.user_config.exists())
        self.assertEqual(unrelated_agent.read_text(encoding="utf-8"), "keep this unrelated role\n")
        for path in expected_paths - {self.user_config}:
            self.assertTrue(path.exists())
            self.assertIn("# Generated by Doozo.", path.read_text(encoding="utf-8"))

        before = {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in expected_paths}
        second = self.output("apply")
        self.assertEqual(second["written"], [])
        self.assertEqual({Path(path) for path in second["unchanged"]}, expected_paths - {self.user_config})
        self.assertEqual(
            {path: (path.read_bytes(), path.stat().st_mtime_ns) for path in expected_paths},
            before,
        )
        self.assertEqual(Path(second["paths"]["user_config"]), self.user_config)
        self.assertEqual(Path(second["paths"]["agents_dir"]), self.agents_dir)

    def test_apply_scope_does_not_render_project_or_invocation_overrides_personally(self) -> None:
        self.write_json(
            self.project_config,
            {"roles": {"scout": {"model": "project-only", "reasoning_effort": "low"}}},
        )
        project_before = self.project_config.read_bytes()
        output = self.output("apply")
        scout = self.agents_dir / "doo-scout.toml"
        self.assertIn('model = "gpt-5.6-terra"', scout.read_text(encoding="utf-8"))
        self.assertEqual(output["effective"]["roles"]["scout"]["model"], "gpt-5.6-terra")
        self.assertEqual(self.project_config.read_bytes(), project_before)

        invocation = self.root / "invocation.json"
        self.write_json(invocation, {"roles": {"scout": {"model": "ephemeral"}}})
        before = scout.read_bytes()
        result = self.run_cli("apply", "--invocation-json", str(invocation), expect=2)
        self.assertIn("only supported by resolve and validate", result.stderr)
        self.assertEqual(scout.read_bytes(), before)

    def test_project_apply_uses_project_agents_by_default(self) -> None:
        project_root = self.root / "project"
        project_root.mkdir()
        settings = self.root / "project-settings.json"
        self.write_json(settings, {"max_workers": 1})

        output = self.output(
            "apply",
            "--write-scope",
            "project",
            "--settings-json",
            str(settings),
            cwd=project_root,
            use_default_agents=True,
        )
        project_agents = project_root / ".codex" / "agents"
        self.assertEqual(Path(output["paths"]["agents_dir"]).resolve(), project_agents.resolve())
        self.assertTrue((project_agents / "doo-scout.toml").exists())
        self.assertTrue(self.project_config.exists())
        self.assertFalse(self.user_config.exists())
        self.assertFalse(self.agents_dir.exists())

    def test_changed_owned_outputs_have_recoverable_backups(self) -> None:
        self.output("apply")
        before_user = self.user_config.read_bytes()
        scout = self.agents_dir / "doo-scout.toml"
        before_scout = scout.read_bytes()
        settings = self.root / "settings.json"
        self.write_json(
            settings,
            {"roles": {"scout": {"model": "gpt-5.5", "reasoning_effort": "high"}}},
        )

        output = self.output("apply", "--settings-json", str(settings))
        user_backup = self.user_config.with_name(f"{self.user_config.name}.bak")
        scout_backup = scout.with_name(f"{scout.name}.bak")
        self.assertEqual({Path(path) for path in output["backups"]}, {user_backup, scout_backup})
        self.assertEqual(user_backup.read_bytes(), before_user)
        self.assertEqual(scout_backup.read_bytes(), before_scout)

        user_before_collision = self.user_config.read_bytes()
        user_backup.write_text("manual backup\n", encoding="utf-8")
        self.write_json(settings, {"max_workers": 1})
        result = self.run_cli("apply", "--settings-json", str(settings), expect=2)
        self.assertIn("backup file was manually modified or collides", result.stderr)
        self.assertEqual(self.user_config.read_bytes(), user_before_collision)

    def test_collisions_and_manual_edits_fail_before_any_write(self) -> None:
        manual_agent = self.agents_dir / "doo-reviewer.toml"
        manual_agent.parent.mkdir(parents=True)
        manual_agent.write_text("manual file\n", encoding="utf-8")

        result = self.run_cli("apply", expect=2)
        self.assertIn("manually modified or collides", result.stderr)
        self.assertFalse(self.user_config.exists())
        self.assertFalse((self.agents_dir / "doo-scout.toml").exists())
        self.assertEqual(manual_agent.read_text(encoding="utf-8"), "manual file\n")

        manual_agent.unlink()
        self.output("apply")
        edited_agent = self.agents_dir / "doo-scout.toml"
        edited_agent.write_text(edited_agent.read_text(encoding="utf-8") + "# manual edit\n", encoding="utf-8")
        before_user = self.user_config.read_bytes()
        before_reviewer = (self.agents_dir / "doo-reviewer.toml").read_bytes()
        settings = self.root / "settings.json"
        self.write_json(settings, {"max_workers": 1})

        result = self.run_cli("apply", "--settings-json", str(settings), expect=2)
        self.assertIn("manually modified or collides", result.stderr)
        self.assertEqual(self.user_config.read_bytes(), before_user)
        self.assertEqual((self.agents_dir / "doo-reviewer.toml").read_bytes(), before_reviewer)


if __name__ == "__main__":
    unittest.main()
