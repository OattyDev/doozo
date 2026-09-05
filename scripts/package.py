#!/usr/bin/env python3
"""Build a portable Codex marketplace archive from the plugin source."""

import argparse
import json
from pathlib import Path
import zipfile


def package(root: Path, output: Path) -> Path:
    manifest = json.loads((root / ".codex-plugin/plugin.json").read_text())
    name = manifest["name"]
    version = manifest["version"]
    if name != "doozo" or any(c not in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-+" for c in version):
        raise ValueError("Expected the doozo manifest with a safe version")
    required = [".codex-plugin/plugin.json", "defaults.json", "skills/doo/SKILL.md", "skills/setup-doo/SKILL.md", "README.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "provenance.json"]
    for relative in required:
        if not (root / relative).is_file():
            raise ValueError(f"Missing required file: {relative}")
    prefix = "doozo-marketplace"
    marketplace = {
        "name": "doozo-local",
        "interface": {"displayName": "Doozo"},
        "plugins": [{
            "name": name,
            "source": {"source": "local", "path": "./plugins/doozo"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }],
    }
    files = set(root / p for p in required)
    for directory in [".codex-plugin", "skills", "scripts", "licenses"]:
        for path in (root / directory).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix in {".md", ".yaml", ".yml", ".json", ".py", ".txt", ".png"}:
                files.add(path)
    interface = manifest.get("interface", {})
    assets = [interface.get(key) for key in ("composerIcon", "logo", "logoDark")]
    assets.extend(interface.get("screenshots", []))
    for relative in filter(None, assets):
        path = root / relative
        if not path.is_file():
            raise ValueError(f"Missing declared image: {relative}")
        files.add(path)
    for path in files:
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Package source escapes plugin: {path}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"{prefix}/.agents/plugins/marketplace.json", json.dumps(marketplace, indent=2) + "\n")
        for path in sorted(files):
            archive.write(path, f"{prefix}/plugins/doozo/{path.relative_to(root).as_posix()}")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New archive path; existing files are never overwritten")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    version = json.loads((root / ".codex-plugin/plugin.json").read_text())["version"]
    try:
        print(package(root, args.output or root / "dist" / f"doozo-{version}.zip"))
    except (ValueError, OSError) as error:
        parser.exit(2, f"Package failed: {error}\n")
