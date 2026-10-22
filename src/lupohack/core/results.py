"""Normalized operation and report model."""

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from lupohack import __version__


@dataclass
class Result:
    module: str
    operation: str
    target: str = ""
    status: str = "SUCCESS"
    summary: str = ""
    findings: list[Any] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    tool: str = "LupoHack"
    tool_version: str = __version__

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
