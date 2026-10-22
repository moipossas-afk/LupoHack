"""Controlled external process execution; no shell, with timeouts and bounded output buffers."""

from __future__ import annotations

import subprocess
import threading
from dataclasses import dataclass


@dataclass
class ProcessResult:
    argv: list[str]
    returncode: int | None
    stdout: str
    stderr: str
    status: str
    error: str | None = None


def _reader(stream, output: bytearray, limit: int) -> None:
    while chunk := stream.read(8192):
        remaining = limit - len(output)
        if remaining > 0:
            output.extend(chunk[:remaining])


def run_process(
    argv: list[str], timeout: float = 30.0, max_output_bytes: int = 1_000_000
) -> ProcessResult:
    if not argv or not argv[0] or not 0 < timeout <= 600:
        raise ValueError("Invalid command or timeout.")
    if not 1 <= max_output_bytes <= 5_000_000:
        raise ValueError("Invalid output limit.")
    try:
        proc = subprocess.Popen(argv, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError as exc:
        return ProcessResult(argv, None, "", "", "MISSING", str(exc))
    except OSError as exc:
        return ProcessResult(argv, None, "", "", "FAILED", str(exc))
    out, err = bytearray(), bytearray()
    threads = [
        threading.Thread(target=_reader, args=(proc.stdout, out, max_output_bytes), daemon=True),
        threading.Thread(target=_reader, args=(proc.stderr, err, max_output_bytes), daemon=True),
    ]
    for thread in threads:
        thread.start()
    try:
        proc.wait(timeout=timeout)
        status, error = ("SUCCESS" if proc.returncode == 0 else "FAILED"), None
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        status, error = "TIMEOUT", f"Timed out after {timeout}s."
    except KeyboardInterrupt:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        status, error = "CANCELLED", "External process interrupted by the user and terminated."
    for thread in threads:
        thread.join(timeout=2)
    stdout = out.decode("utf-8", errors="replace")
    stderr = err.decode("utf-8", errors="replace")
    if len(out) >= max_output_bytes:
        stdout += "\n[OUTPUT TRUNCATED AT THE CONFIGURED LIMIT]"
    if len(err) >= max_output_bytes:
        stderr += "\n[OUTPUT TRUNCATED AT THE CONFIGURED LIMIT]"
    return ProcessResult(
        argv,
        proc.returncode if status not in ("TIMEOUT", "CANCELLED") else None,
        stdout,
        stderr,
        status,
        error,
    )
