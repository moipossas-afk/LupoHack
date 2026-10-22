"""Public DNS and RDAP lookups with source attribution and per-record-type results."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

import dns.exception
import dns.resolver

from lupohack.core.validation import validate_domain

_RDAP = "https://rdap.org/domain/"
DNS_TYPES = ("A", "AAAA", "MX", "NS", "TXT", "CNAME")


def dns_records(domain: str, timeout: float = 4.0) -> dict:
    """Query A/AAAA/MX/NS/TXT/CNAME records; each type reports its own status."""
    d = validate_domain(domain)
    if not 0 < timeout <= 15:
        raise ValueError("DNS timeout must be greater than 0 and at most 15 seconds.")
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout
    records: dict[str, dict] = {}
    for record_type in DNS_TYPES:
        try:
            answer = resolver.resolve(d, record_type, lifetime=timeout, raise_on_no_answer=False)
            if answer.rrset is None:
                records[record_type] = {"status": "NO_ANSWER", "values": []}
                continue
            values = []
            for item in answer:
                if record_type == "MX":
                    values.append(
                        {"priority": item.preference, "exchange": item.exchange.to_text()}
                    )
                elif record_type == "TXT":
                    values.append(
                        "".join(part.decode("utf-8", errors="replace") for part in item.strings)
                    )
                else:
                    values.append(item.to_text())
            records[record_type] = {"status": "SUCCESS", "values": values}
        except dns.resolver.NXDOMAIN:
            records[record_type] = {
                "status": "NXDOMAIN",
                "values": [],
                "error": "Domain does not exist.",
            }
        except dns.resolver.NoAnswer:
            records[record_type] = {"status": "NO_ANSWER", "values": []}
        except dns.exception.Timeout:
            records[record_type] = {
                "status": "TIMEOUT",
                "values": [],
                "error": f"Timed out after {timeout}s.",
            }
        except dns.resolver.NoNameservers as exc:
            records[record_type] = {"status": "DNS_ERROR", "values": [], "error": str(exc)}
        except dns.exception.DNSException as exc:
            records[record_type] = {"status": "DNS_ERROR", "values": [], "error": str(exc)}
    statuses = {v["status"] for v in records.values()}
    overall = (
        "SUCCESS"
        if "SUCCESS" in statuses
        else ("FAILED" if statuses <= {"NXDOMAIN", "DNS_ERROR", "TIMEOUT"} else "PARTIAL")
    )
    return {
        "domain": d,
        "source": "System-configured DNS resolver",
        "status": overall,
        "timeout_seconds": timeout,
        "records": records,
    }


def rdap_lookup(domain: str, timeout: float = 8.0) -> dict:
    d = validate_domain(domain)
    req = urllib.request.Request(
        _RDAP + d,
        headers={
            "User-Agent": "LupoHack/1.0 (public RDAP lookup)",
            "Accept": "application/rdap+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if r.status != 200:
                return {
                    "domain": d,
                    "status": "FAILED",
                    "error": f"HTTP {r.status}",
                    "source": req.full_url,
                }
            body = r.read(512 * 1024 + 1)
            if len(body) > 512 * 1024:
                return {
                    "domain": d,
                    "status": "FAILED",
                    "error": "RDAP response exceeds the 512 KiB limit.",
                    "source": req.full_url,
                }
            data = json.loads(body)
            return {"domain": d, "status": "SUCCESS", "source": r.geturl(), "data": data}
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as e:
        return {
            "domain": d,
            "status": "FAILED",
            "error": str(e),
            "source": req.full_url,
            "limitation": "Public sources may rate-limit requests or omit data.",
        }
