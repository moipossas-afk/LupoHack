"""Conservative HTTP(S) inspection that blocks non-public destinations and redirects."""

import ipaddress
import socket
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from lupohack.core.validation import validate_url

HEADERS = (
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "X-Frame-Options",
)


def _public_destination(url: str) -> None:
    u = urlsplit(validate_url(url))
    host = u.hostname or ""
    try:
        ips = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            ips = [
                ipaddress.ip_address(x[4][0])
                for x in socket.getaddrinfo(
                    host, u.port or (443 if u.scheme == "https" else 80), type=socket.SOCK_STREAM
                )
            ]
        except OSError as e:
            raise ValueError(f"Could not validate destination DNS: {e}") from e
    if not ips or any(not x.is_global for x in ips):
        raise ValueError(
            "Blocked a local, private, reserved, or non-public destination (SSRF protection)."
        )


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def inspect_url(url: str, timeout: float = 8.0, max_redirects: int = 3) -> dict:
    current = validate_url(url)
    started = time.monotonic()
    redirects = []
    if not 0 < timeout <= 20 or not 0 <= max_redirects <= 5:
        raise ValueError(
            "Timeout must be greater than 0 and at most 20 seconds; max_redirects must be from 0 to 5."
        )
    for _ in range(max_redirects + 1):
        _public_destination(current)
        req = Request(
            current,
            method="GET",
            headers={
                "User-Agent": "LupoHack/1.0 (authorized basic inspection)",
                "Range": "bytes=0-0",
            },
        )
        try:
            with build_opener(_NoRedirect).open(req, timeout=timeout) as resp:
                status = resp.status
                headers = dict(resp.headers.items())
                final = resp.geturl()
        except HTTPError as e:
            if e.code in (301, 302, 303, 307, 308):
                loc = e.headers.get("Location")
                if not loc:
                    break
                nxt = validate_url(urljoin(current, loc))
                _public_destination(nxt)
                redirects.append({"from": current, "to": nxt, "status": e.code})
                current = nxt
                continue
            error = f"HTTP {e.code}"
        except (URLError, TimeoutError, OSError) as e:
            error = str(e)
        else:
            error = None
        if error is not None:
            return {
                "url": current,
                "status": "FAILED",
                "error": error,
                "elapsed_ms": round((time.monotonic() - started) * 1000, 2),
                "limitations": ["Non-invasive check; does not assess vulnerabilities."],
            }
        sec = {h: headers.get(h) for h in HEADERS}
        present = [h for h, v in sec.items() if v]
        return {
            "url": url,
            "final_url": final,
            "http_status": status,
            "headers": sec,
            "missing_headers": [h for h in HEADERS if h not in present],
            "redirects": redirects,
            "elapsed_ms": round((time.monotonic() - started) * 1000, 2),
            "tls": "Validated by Python’s default HTTPS client."
            if urlsplit(final).scheme == "https"
            else "Not applicable (HTTP)",
            "limitations": [
                "A missing header alone is not proof of a vulnerability.",
                "Response is limited to a GET request with Range; servers may ignore Range.",
            ],
        }
