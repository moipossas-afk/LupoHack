"""Diagnostics based on the actual environment and adapter status."""

import os
import platform
import sys

from lupohack import __version__
from lupohack.core.store import data_dir
from lupohack.integrations.tool_manager import check_all


def diagnostics() -> dict:
    d = data_dir()
    tools = check_all()
    by_id = {item["id"]: item for item in tools}
    sherlock = by_id["sherlock"]["status"]
    dns_dependency = next(item for item in tools if item["id"] == "dnspython")
    return {
        "app_version": __version__,
        "python": platform.python_version(),
        "python_supported": sys.version_info >= (3, 11),
        "os": platform.platform(),
        "architecture": platform.machine(),
        "venv_active": sys.prefix != sys.base_prefix,
        "data_dir": str(d),
        "data_writable": os.access(d, os.W_OK),
        "tools": {
            item["id"]: {
                "status": item["status"],
                "executable": item["executable"],
                "version": item["version"],
                "integration": item["integration"],
            }
            for item in tools
        },
        "modules": {
            "files": "AVAILABLE",
            "network": "AVAILABLE",
            "dns_A_AAAA_MX_NS_TXT_CNAME": "AVAILABLE"
            if dns_dependency["status"] == "AVAILABLE"
            else "UNAVAILABLE (dnspython missing)",
            "rdap": "AVAILABLE (Internet required)",
            "web_inspection": "AVAILABLE (public destinations only)",
            "username_search": "AVAILABLE_LIMITED"
            if sherlock == "AVAILABLE"
            else "UNAVAILABLE (Sherlock missing)",
            "zap": "AVAILABLE_LIMITED"
            if by_id["zap"]["status"] == "AVAILABLE"
            else "UNAVAILABLE (ZAP missing)",
            "metasploit": "AVAILABLE_LIMITED"
            if by_id["metasploit"]["status"] == "AVAILABLE"
            else "UNAVAILABLE (Metasploit missing)",
        },
    }
