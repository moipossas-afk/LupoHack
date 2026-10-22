"""Nmap adapter for conservative TCP discovery on an authorized host."""

from __future__ import annotations

import shutil
import xml.etree.ElementTree as ET

from lupohack.config import load_config
from lupohack.core.validation import validate_ip_or_host
from lupohack.integrations.process import run_process


def executable() -> str | None:
    return shutil.which("nmap")


def scan_authorized_host(target: str, *, authorized: bool, timeout: float = 90.0) -> dict:
    host = validate_ip_or_host(target)
    if not authorized:
        raise PermissionError(
            "Explicitly confirm authorization for the target before running Nmap."
        )
    allowed = load_config()["allowed_targets"]
    if allowed and host not in allowed:
        raise PermissionError("Target is not in the configured allowed_targets list.")
    exe = executable()
    if not exe:
        return {"status": "UNAVAILABLE", "target": host, "error": "Nmap was not found on PATH."}
    if not 5 <= timeout <= 180:
        raise ValueError("Nmap timeout must be between 5 and 180 seconds.")
    argv = [
        exe,
        "-n",
        "-sT",
        "-T2",
        "--top-ports",
        "20",
        "--host-timeout",
        f"{int(timeout)}s",
        "-oX",
        "-",
        host,
    ]
    result = run_process(argv, timeout=timeout + 5, max_output_bytes=2_000_000)
    parsed = []
    if result.stdout:
        try:
            root = ET.fromstring(result.stdout)
            for h in root.findall("host"):
                status = h.find("status")
                addresses = [
                    {"addr": a.get("addr"), "type": a.get("addrtype")} for a in h.findall("address")
                ]
                ports = []
                for port in h.findall("./ports/port"):
                    state = port.find("state")
                    service = port.find("service")
                    ports.append(
                        {
                            "protocol": port.get("protocol"),
                            "port": int(port.get("port", "0")),
                            "state": state.get("state") if state is not None else "unknown",
                            "service": service.get("name") if service is not None else None,
                        }
                    )
                parsed.append(
                    {
                        "status": status.get("state") if status is not None else "unknown",
                        "addresses": addresses,
                        "ports": ports,
                    }
                )
        except (ET.ParseError, ValueError) as exc:
            return {
                "status": "PARTIAL",
                "target": host,
                "error": f"Invalid Nmap XML: {exc}",
                "returncode": result.returncode,
                "stdout": result.stdout[:100_000],
                "stderr": result.stderr[:20_000],
            }
    final_status = (
        result.status
        if result.status in {"FAILED", "TIMEOUT", "CANCELLED", "MISSING"}
        else "SUCCESS"
        if parsed
        else "PARTIAL"
    )
    return {
        "status": final_status,
        "target": host,
        "tool": "Nmap",
        "returncode": result.returncode,
        "hosts": parsed,
        "stderr": result.stderr[:20_000],
        "error": result.error,
        "scope": "one host; TCP connect; top 20 ports; no vulnerability scripts",
        "warning": "An open port is not, by itself, a vulnerability.",
    }
