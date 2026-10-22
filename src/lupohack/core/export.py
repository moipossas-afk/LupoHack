"""JSON, CSV, and text summary exports."""

import csv
import json
from pathlib import Path

from lupohack.core.results import Result


def export_result(result: Result | dict, path: str | Path, fmt: str | None = None) -> Path:
    row = result.to_dict() if isinstance(result, Result) else result
    dest = Path(path).expanduser()
    fmt = (fmt or dest.suffix.lstrip(".")).lower()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        dest.write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
    elif fmt == "csv":
        with dest.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(row))
            w.writeheader()
            w.writerow(
                {
                    k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v
                    for k, v in row.items()
                }
            )
    elif fmt == "txt":
        dest.write_text(
            f"LupoHack — {row.get('module')} / {row.get('operation')}\nStatus: {row.get('status')}\nTarget: {row.get('target')}\nSummary: {row.get('summary')}\nWarnings: {'; '.join(row.get('warnings', []))}\nErrors: {'; '.join(row.get('errors', []))}\n",
            encoding="utf-8",
        )
    else:
        raise ValueError("Supported formats: json, csv, or txt.")
    return dest
