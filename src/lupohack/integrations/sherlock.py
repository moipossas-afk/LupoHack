"""Sherlock adapter for bounded searches of public usernames."""

from __future__ import annotations

import re
import shutil

from lupohack.core.validation import validate_username
from lupohack.integrations.process import run_process

URL_RE = re.compile(r"https?://[^\s\]>)]+", re.IGNORECASE)


def executable() -> str | None:
    return shutil.which("sherlock")


def search_username(username: str, timeout: float = 120.0) -> dict:
    name = validate_username(username)
    exe = executable()
    if not exe:
        return {
            "status": "UNAVAILABLE",
            "username": name,
            "error": "Sherlock was not found on PATH. See the installation guide.",
            "profiles": [],
            "tool": "Sherlock",
        }
    if not 1 <= timeout <= 300:
        raise ValueError("Sherlock timeout must be between 1 and 300 seconds.")
    result = run_process(
        [exe, name, "--print-found", "--timeout", "10"],
        timeout=timeout,
        max_output_bytes=1_000_000,
    )
    urls = sorted(set(URL_RE.findall(result.stdout)))
    return {
        "status": result.status,
        "username": name,
        "tool": "Sherlock",
        "executable": exe,
        "returncode": result.returncode,
        "outcome": "MATCHES_REPORTED"
        if urls
        else ("NO_MATCH_REPORTED" if result.status == "SUCCESS" else "INCONCLUSIVE"),
        "profiles": [{"url": url, "status": "FOUND_REPORTED_BY_TOOL"} for url in urls],
        "stdout": result.stdout[:200_000],
        "stderr": result.stderr[:20_000],
        "error": result.error,
        "limitation": "Profiles with the same username are not proof of identity; websites may block requests or change.",
    }
