"""Bounded TLS certificate inspection for explicitly authorized hosts."""

from __future__ import annotations

import socket
import ssl
import time
from datetime import UTC, datetime

from lupohack.core.validation import validate_ip_or_host, validate_port


def inspect_tls(host: str, port: int = 443, timeout: float = 5.0) -> dict:
    """Connect with standard certificate verification and report peer metadata.

    This performs one TLS handshake only. It does not scan alternate ports or
    weaken certificate/hostname validation.
    """
    host = validate_ip_or_host(host)
    port = validate_port(port)
    if not 0 < timeout <= 15:
        raise ValueError("Timeout must be greater than 0 and at most 15 seconds.")

    started = time.monotonic()
    context = ssl.create_default_context()
    try:
        with (
            socket.create_connection((host, port), timeout=timeout) as connection,
            context.wrap_socket(connection, server_hostname=host) as tls_socket,
        ):
            certificate = tls_socket.getpeercert()
            if not certificate:
                return {
                    "host": host,
                    "port": port,
                    "status": "FAILED",
                    "error": "The peer did not provide a certificate.",
                    "elapsed_ms": round((time.monotonic() - started) * 1000, 2),
                }
            not_after = certificate.get("notAfter")
            expiry = (
                datetime.fromtimestamp(ssl.cert_time_to_seconds(not_after), UTC)
                if not_after
                else None
            )
            now = datetime.now(UTC)
            cipher = tls_socket.cipher()
            return {
                "host": host,
                "port": port,
                "status": "VERIFIED",
                "certificate_validation": "PASSED",
                "tls_version": tls_socket.version(),
                "cipher": cipher[0] if cipher else None,
                "subject": certificate.get("subject", ()),
                "issuer": certificate.get("issuer", ()),
                "subject_alt_names": [
                    name
                    for kind, name in certificate.get("subjectAltName", ())
                    if kind in ("DNS", "IP Address")
                ],
                "not_before": certificate.get("notBefore"),
                "not_after": not_after,
                "expires_in_days": (expiry - now).total_seconds() / 86400 if expiry else None,
                "elapsed_ms": round((time.monotonic() - started) * 1000, 2),
                "limitations": [
                    "One TLS handshake only; no port scan or cryptographic audit was performed.",
                    "Certificate validation uses the active Python/OpenSSL trust store.",
                ],
            }
    except (OSError, ssl.SSLError, TimeoutError, ValueError) as exc:
        return {
            "host": host,
            "port": port,
            "status": "FAILED",
            "certificate_validation": "FAILED_OR_UNAVAILABLE",
            "error": str(exc),
            "elapsed_ms": round((time.monotonic() - started) * 1000, 2),
        }
