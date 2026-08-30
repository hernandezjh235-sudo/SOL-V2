#!/usr/bin/env python3
from __future__ import annotations

import os
import py_compile
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "app.py"
RUNTIME = ROOT / "runtime_app.py"

# SOL V2's checked-in app.py is the frozen experimental K candidate.
# Runtime operational guards are applied only to a disposable runtime copy so
# Save/Refresh/Savant/cache behavior matches Challenger without mutating the
# SOL V2 source or reapplying Challenger K / Moneyline / Pitching Outs patches.
shutil.copy2(SOURCE, RUNTIME)

# IMPORTANT: operational/runtime-only patches. Do not add K/ML/PO model patches.
PATCHES = [
    "tools/apply_runtime_stability_v1.py",
    "tools/apply_manual_refresh_state_v2.py",
    "tools/apply_savant_manual_only_v3.py",
    "tools/apply_recency_cache_guard_v3.py",
    "tools/apply_recency_lazy_guard_v2.py",
]

for rel in PATCHES:
    script = ROOT / rel
    if not script.exists():
        raise FileNotFoundError(f"Required SOL V2 runtime guard missing: {rel}")
    subprocess.run(
        [sys.executable, str(script), "--app", str(RUNTIME)],
        cwd=str(ROOT),
        check=True,
    )

py_compile.compile(str(RUNTIME), doraise=True)

# Keep Streamlit source watching disabled, matching Challenger's stable runtime
# behavior and preventing data/cache writes from becoming source reload loops.
os.environ.setdefault("STREAMLIT_SERVER_FILE_WATCHER_TYPE", "none")
os.environ.setdefault("STREAMLIT_SERVER_RUN_ON_SAVE", "false")
port = str(os.environ.get("PORT") or "8080")

cmd = [
    "streamlit", "run", str(RUNTIME),
    "--server.port", port,
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--server.fileWatcherType", "none",
    "--server.runOnSave", "false",
]
os.execvp(cmd[0], cmd)
