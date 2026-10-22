"""Validated local JSON configuration with atomic updates."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from lupohack.core.validation import validate_ip_or_host

DEFAULTS = {
    "language": "en",
    "theme": "dark",
    "default_timeout_seconds": 8,
    "history_enabled": True,
    "require_scope_confirmation": True,
    "allowed_targets": [],
    "allow_external_targets": False,
}


class ConfigError(ValueError):
    pass


def config_path() -> Path:
    if os.environ.get("XDG_CONFIG_HOME"):
        base = Path(os.environ["XDG_CONFIG_HOME"])
    elif os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))
    else:
        base = Path.home() / ".config"
    return base / "lupohack" / "config.json"


def validate_config(value: dict) -> dict:
    if not isinstance(value, dict):
        raise ConfigError("Configuration must be a JSON object.")
    merged = {**DEFAULTS, **value}
    if merged["language"] == "pt":
        merged["language"] = "en"  # Migrate legacy Portuguese configuration to English.
    if merged["language"] != "en":
        raise ConfigError("language must be en.")
    if merged["theme"] not in ("dark", "light"):
        raise ConfigError("theme must be dark or light.")
    if (
        isinstance(merged["default_timeout_seconds"], bool)
        or not isinstance(merged["default_timeout_seconds"], int)
        or not 1 <= merged["default_timeout_seconds"] <= 30
    ):
        raise ConfigError("default_timeout_seconds must be an integer from 1 to 30.")
    for key in ("history_enabled", "require_scope_confirmation", "allow_external_targets"):
        if not isinstance(merged[key], bool):
            raise ConfigError(f"{key} must be a boolean.")
    targets = merged["allowed_targets"]
    if not isinstance(targets, list) or len(targets) > 100:
        raise ConfigError("allowed_targets must be a list of up to 100 hosts or domains.")
    try:
        merged["allowed_targets"] = sorted({validate_ip_or_host(t) for t in targets})
    except (ValueError, TypeError) as exc:
        raise ConfigError(f"Invalid allowed_targets: {exc}") from exc
    unknown = set(value) - set(DEFAULTS)
    if unknown:
        raise ConfigError(f"Unknown fields: {', '.join(sorted(unknown))}")
    return merged


def load_config() -> dict:
    path = config_path()
    if not path.exists():
        return DEFAULTS.copy()
    try:
        return validate_config(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Could not read {path}: {exc}") from exc


def save_config(value: dict) -> Path:
    validated = validate_config(value)
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix="config-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(validated, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
    return path


def set_config_value(key: str, raw_value: str) -> dict:
    if key not in DEFAULTS:
        raise ConfigError(f"Unknown or non-editable field: {key}")
    current = load_config()
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ConfigError('Value must be JSON, for example 10, true, or ["host.example"].') from exc
    current[key] = value
    save_config(current)
    return load_config()
