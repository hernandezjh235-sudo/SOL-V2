#!/usr/bin/env python3
from __future__ import annotations

"""SOL V2 Railway launcher.

The checked-in app.py is now a complete, integrated App 130 + SOL V2 build.
Do NOT re-apply legacy Challenger runtime patch scripts over it at boot.
Those patches were designed for an older source app and can fail or duplicate
logic already embedded in the current full app.

This launcher therefore:
1) compiles app.py as a boot smoke test;
2) sets conservative Streamlit runtime flags; and
3) launches app.py directly.

This changes deployment/runtime plumbing only. It does not modify Challenger
K logic or SOL V2 workload/start-shape calculations.
"""

import os
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP = ROOT / "app.py"

if not APP.exists():
    raise FileNotFoundError(f"SOL V2 app missing: {APP}")

# Fail fast on a real syntax problem, rather than partially starting Railway.
py_compile.compile(str(APP), doraise=True)
print("SOL V2 boot smoke: app.py compiled successfully")
print("SOL V2 boot mode: direct integrated app.py (legacy runtime patches skipped)")

os.environ.setdefault("STREAMLIT_SERVER_FILE_WATCHER_TYPE", "none")
os.environ.setdefault("STREAMLIT_SERVER_RUN_ON_SAVE", "false")
port = str(os.environ.get("PORT") or "8080")

cmd = [
    "streamlit", "run", str(APP),
    "--server.port", port,
    "--server.address", "0.0.0.0",
    "--server.headless", "true",
    "--server.fileWatcherType", "none",
    "--server.runOnSave", "false",
]

os.execvp(cmd[0], cmd)
