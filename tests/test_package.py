import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile


MODULE = Path(__file__).resolve().parents[1] / "scripts/package.py"
spec = importlib.util.spec_from_file_location("doozo_package", MODULE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PackageTests(unittest.TestCase):
    def fixture(self, root):
        for relative in ["defaults.json", "skills/doo/SKILL.md", "skills/setup-doo/SKILL.md", "README.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "provenance.json"]:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}")
        (root / ".codex-plugin").mkdir()
        (root / ".codex-plugin/plugin.json").write_text(json.dumps({"name": "doozo", "version": "0.1.0"}))

    def test_relocated_marketplace_resolves_and_excludes_local_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "source"
            self.fixture(root)
            (root / ".env").write_text("PRIVATE")
            (root / "skills/.env").write_text("PRIVATE")
            (root / ".doozo").mkdir()
            (root / ".doozo/config.json").write_text("PRIVATE")
            archive = module.package(root, Path(directory) / "bundle.zip")
            with zipfile.ZipFile(archive) as z:
                self.assertFalse(any(".env" in n or "/.doozo/" in n for n in z.namelist()))
                z.extractall(Path(directory) / "relocated")
            relocated = Path(directory) / "relocated/doozo-marketplace"
            catalog = json.loads((relocated / ".agents/plugins/marketplace.json").read_text())
            plugin = relocated / catalog["plugins"][0]["source"]["path"]
            self.assertEqual(json.loads((plugin / ".codex-plugin/plugin.json").read_text())["name"], "doozo")
            self.assertTrue((plugin / "skills/doo/SKILL.md").is_file())
            self.assertFalse((plugin / "evals").exists())
            self.assertFalse((plugin / "tests").exists())

    def test_existing_archive_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "source"
            self.fixture(root)
            archive = Path(directory) / "bundle.zip"
            archive.write_bytes(b"keep")
            with self.assertRaises(FileExistsError):
                module.package(root, archive)
            self.assertEqual(archive.read_bytes(), b"keep")

    def test_required_file_symlink_is_rejected_before_archive_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "source"
            self.fixture(root)
            target = Path(directory) / "private.json"
            target.write_text("PRIVATE")
            (root / "defaults.json").unlink()
            (root / "defaults.json").symlink_to(target)
            archive = Path(directory) / "bundle.zip"
            with self.assertRaises(ValueError):
                module.package(root, archive)
            self.assertFalse(archive.exists())


if __name__ == "__main__":
    unittest.main()
