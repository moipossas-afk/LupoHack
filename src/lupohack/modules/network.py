"""DNS/TCP diagnostics. TCP checks connectivity only; it does not test for vulnerabilities."""

import socket
import time

from lupohack.core.validation import validate_ip_or_host, validate_port


def dns_lookup(host: str) -> dict:
    host = validate_ip_or_host(host)
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        return {"host": host, "addresses": sorted({i[4][0] for i in infos}), "status": "SUCCESS"}
    except socket.gaierror as exc:
        return {"host": host, "addresses": [], "status": "FAILED", "error": str(exc)}


def tcp_check(host: str, port: int, timeout: float = 3.0) -> dict:
    host = validate_ip_or_host(host)
    port = validate_port(port)
    if not 0 < timeout <= 15:
        raise ValueError("Timeout must be greater than 0 and at most 15 seconds.")
    start = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            pass
        return {
            "host": host,
            "port": port,
            "status": "REACHABLE",
            "elapsed_ms": round((time.monotonic() - start) * 1000, 2),
            "note": "TCP connection established; this does not determine whether the host is vulnerable.",
        }
    except OSError as exc:
        return {
            "host": host,
            "port": port,
            "status": "UNREACHABLE_OR_FILTERED",
            "elapsed_ms": round((time.monotonic() - start) * 1000, 2),
            "error": str(exc),
            "note": "A connection failure does not prove that the system is offline.",
        }
