"""Local persistence in the user data directory."""

import json
import os
from pathlib import Path
from platform import system

from lupohack.core.results import Result


def data_dir() -> Path:
    if os.environ.get("XDG_DATA_HOME"):
        base = Path(os.environ["XDG_DATA_HOME"])
    elif system() == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    elif system() == "Darwin":
        base = Path.home() / "Library/Application Support"
    else:
        base = Path.home() / ".local/share"
    d = base / "lupohack"
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_result(result: Result) -> Path:
    d = data_dir() / "history"
    d.mkdir(parents=True, exist_ok=True)
    path = d / (result.id + ".json")
    path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def history(module: str | None = None) -> list[dict]:
    d = data_dir() / "history"
    rows = []
    if d.exists():
        for f in sorted(d.glob("*.json")):
            try:
                r = json.loads(f.read_text(encoding="utf-8"))
                if module is None or r.get("module") == module:
                    rows.append(r)
            except (OSError, json.JSONDecodeError):
                continue
    return rows


def clear_history() -> int:
    d = data_dir() / "history"
    fs = list(d.glob("*.json")) if d.exists() else []
    for f in fs:
        f.unlink()
    return len(fs)
