"""Confirmed local launch for ZAP and Metasploit; no automatic scans or exploits."""

from __future__ import annotations

import os
import subprocess

from lupohack.integrations.tool_manager import CATALOG, inspect_tool


def launch_tool(name: str, *, confirmed: bool) -> dict:
    key = name.lower()
    if key not in ("zap", "metasploit"):
        raise ValueError("This workflow can launch only OWASP ZAP or Metasploit Framework.")
    if not confirmed:
        return {
            "status": "CANCELLED",
            "message": "Launch cancelled; explicit confirmation is required.",
        }
    info = inspect_tool(key)
    if info["status"] != "AVAILABLE":
        return {
            "status": "UNAVAILABLE",
            "tool": CATALOG[key]["display"],
            "message": "Executable was not found on PATH.",
        }
    argv = [info["executable"]]
    try:
        if key == "metasploit":
            # Runs in the foreground with the inherited TTY; no scripts, targets, or modules are supplied.
            completed = subprocess.run(argv, shell=False, check=False)
            return {
                "status": "EXITED",
                "tool": CATALOG[key]["display"],
                "returncode": completed.returncode,
                "note": "LupoHack supplied no target, script, exploit, or command.",
            }
        # Launches the ZAP GUI separately without scan, target, or API arguments.
        kwargs = {
            "shell": False,
            "stdin": subprocess.DEVNULL,
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if os.name == "nt":
            kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        else:
            kwargs["start_new_session"] = True
        process = subprocess.Popen(argv, **kwargs)
        return {
            "status": "LAUNCHED",
            "tool": CATALOG[key]["display"],
            "pid": process.pid,
            "argv": argv,
            "note": "No target or scan was supplied.",
        }
    except OSError as exc:
        return {"status": "FAILED", "tool": CATALOG[key]["display"], "error": str(exc)}
    except KeyboardInterrupt:
        return {
            "status": "CANCELLED",
            "tool": CATALOG[key]["display"],
            "note": "Launch interrupted by the user.",
        }
