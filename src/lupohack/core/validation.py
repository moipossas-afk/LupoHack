"""Centralized input validation with conservative policies."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

_DOMAIN = re.compile(
    r"(?=.{1,253}\.?$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)*[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.?$"
)


def validate_domain(value: str) -> str:
    value = value.strip().rstrip(".")
    if not value or not _DOMAIN.fullmatch(value):
        raise ValueError("Invalid domain.")
    return value.encode("idna").decode("ascii").lower()


def validate_ip_or_host(value: str) -> str:
    value = value.strip()
    if not value or any(c in value for c in "/\\@?#") or value.startswith("-"):
        raise ValueError("Invalid host.")
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        return validate_domain(value)


def validate_network(value: str) -> str:
    try:
        return str(ipaddress.ip_network(value, strict=False))
    except ValueError as exc:
        raise ValueError("Invalid CIDR network.") from exc


def validate_port(port: int) -> int:
    if isinstance(port, bool) or not 1 <= int(port) <= 65535:
        raise ValueError("Port must be between 1 and 65535.")
    return int(port)


def validate_url(value: str) -> str:
    u = urlsplit(value.strip())
    if u.scheme not in ("http", "https") or not u.hostname or u.username or u.password:
        raise ValueError("Invalid URL: use HTTP/HTTPS and do not include credentials.")
    validate_ip_or_host(u.hostname)
    if u.port is not None:
        validate_port(u.port)
    return u.geturl()


def validate_username(value: str) -> str:
    v = value.strip()
    if v.startswith("-") or not re.fullmatch(r"[A-Za-z0-9._-]{1,39}", v):
        raise ValueError(
            "Username must be 1–39 characters and may contain letters, numbers, periods, hyphens, or underscores."
        )
    return v
