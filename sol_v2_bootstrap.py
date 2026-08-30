#!/usr/bin/env python3
"""Populate SOL V2 with the pinned Challenger support snapshot without touching Challenger.

This script is safe for a brand-new repository or Railway service:
- Reads a public, pinned Challenger commit archive.
- Copies supporting files/data/tools into THIS repository only.
- Never overwrites SOL V2 app.py or its frozen baseline.
- Can populate only (GitHub Actions) or populate then launch SOL's isolated
  stable runtime wrapper.
"""
from __future__ import annotations

import argparse
import json
import os
import py_compile
import shutil
import sys
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

BASE_REPO = "hernandezjh235-sudo/chanllger"
BASE_COMMIT = "1e696e484ada2fc4cb8a8a8b71a994e2988bc868"
ARCHIVE_URL = f"https://github.com/{BASE_REPO}/archive/{BASE_COMMIT}.zip"
ROOT = Path(__file__).resolve().parent
MARKER = ROOT / ".sol_v2_support_ready.json"

PROTECTED_TOP_LEVEL = {
    "app.py",
    "SOL_V2_BASELINE_DO_NOT_EDIT.py",
    "sol_v2_bootstrap.py",
    "sol_v2_launch_stable.py",
    "SOL_V2_SETUP_README.md",
    "CHALLENGER_BASE_PIN.txt",
    "Procfile",
    "requirements.txt",
    "runtime.txt",
    "SHA256SUMS.txt",
    ".gitignore",
}

REQUIRED_SUPPORT = [
    "learning_data/graded_history.csv",
    "learning_data/pitch_mix_matchups.csv",
    "learning_data/savant_batter_platoon_2026.csv",
    "learning_data/savant_batter_profiles.csv",
    "learning_data/savant_pitcher_stats.csv",
    "learning_data/savant_refresh_manifest.json",
    "challenger_bootstrap.py",
    "savant_display_bridge.py",
    "tools/launch_stable.py",
    "tools/apply_runtime_stability_v1.py",
    "tools/apply_manual_refresh_state_v2.py",
    "tools/apply_savant_manual_only_v3.py",
]


def _support_complete() -> bool:
    if not MARKER.exists():
        return False
    try:
        data = json.loads(MARKER.read_text(encoding="utf-8"))
        if data.get("base_commit") != BASE_COMMIT:
            return False
    except Exception:
        return False
    return all((ROOT / rel).exists() for rel in REQUIRED_SUPPORT)


def _download_archive(dst: Path) -> None:
    req = urllib.request.Request(
        ARCHIVE_URL,
        headers={"User-Agent": "challenger-sol-v2-bootstrap/1.2"},
    )
    with urllib.request.urlopen(req, timeout=120) as response, dst.open("wb") as fh:
        shutil.copyfileobj(response, fh)


def _copy_support(src_root: Path) -> None:
    for item in src_root.iterdir():
        if item.name in PROTECTED_TOP_LEVEL or item.name == ".git":
            continue

        if item.name == ".github" and item.is_dir():
            dest_gh = ROOT / ".github"
            dest_gh.mkdir(parents=True, exist_ok=True)
            for gh_item in item.iterdir():
                if gh_item.name == "workflows" and gh_item.is_dir():
                    disabled = dest_gh / "challenger_workflows_disabled"
                    shutil.copytree(gh_item, disabled, dirs_exist_ok=True)
                else:
                    gh_dest = dest_gh / gh_item.name
                    if gh_item.is_dir():
                        shutil.copytree(gh_item, gh_dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(gh_item, gh_dest)
            continue

        dest = ROOT / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)


def populate(force: bool = False) -> None:
    if _support_complete() and not force:
        print(f"SOL V2 support already pinned to {BASE_COMMIT}.")
        return

    print(f"Populating SOL V2 support from read-only Challenger commit {BASE_COMMIT}...")
    with tempfile.TemporaryDirectory(prefix="sol_v2_support_") as td:
        td_path = Path(td)
        archive = td_path / "challenger.zip"
        _download_archive(archive)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(td_path / "extract")
        roots = [p for p in (td_path / "extract").iterdir() if p.is_dir()]
        if len(roots) != 1:
            raise RuntimeError(f"Unexpected Challenger archive layout: {roots}")
        _copy_support(roots[0])

    missing = [rel for rel in REQUIRED_SUPPORT if not (ROOT / rel).exists()]
    if missing:
        raise RuntimeError(f"Support snapshot incomplete; missing: {missing}")

    py_compile.compile(str(ROOT / "app.py"), doraise=True)
    py_compile.compile(str(ROOT / "sol_v2_launch_stable.py"), doraise=True)

    marker = {
        "base_repo": BASE_REPO,
        "base_commit": BASE_COMMIT,
        "populated_at_utc": datetime.now(timezone.utc).isoformat(),
        "app_py_protected": True,
        "runtime_mode": "sol_v2_isolated_stable_launcher",
    }
    MARKER.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")
    print("SOL V2 support population complete. app.py remained protected.")


def launch() -> None:
    launcher = ROOT / "sol_v2_launch_stable.py"
    if not launcher.exists():
        raise FileNotFoundError(f"SOL V2 stable launcher missing: {launcher}")
    os.execv(sys.executable, [sys.executable, str(launcher)])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--populate-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    populate(force=args.force)
    if not args.populate_only:
        launch()


if __name__ == "__main__":
    main()
