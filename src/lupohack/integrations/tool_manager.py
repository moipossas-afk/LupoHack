"""Catalog and safe management of optional external tools."""

from __future__ import annotations

import importlib.metadata
import platform
import shutil

from lupohack.integrations.process import run_process

CATALOG = {
    "sherlock": {
        "display": "Sherlock",
        "executables": ["sherlock"],
        "version_args": ["--version"],
        "purpose": "Search for usernames on public websites",
        "category": "Reconnaissance",
        "modules": ["osint.username"],
        "integration": "IMPLEMENTED_LIMITED",
        "docs": "https://github.com/sherlock-project/sherlock",
        "install": {
            "Linux": "Install with pipx following the project’s official instructions: https://github.com/sherlock-project/sherlock",
            "Windows": "Official installation methods: https://sherlockproject.xyz/installation. LupoHack integration on Windows has not been verified.",
            "Darwin": "Official installation methods: https://sherlockproject.xyz/installation. LupoHack integration on macOS has not been verified.",
        },
    },
    "zap": {
        "display": "OWASP ZAP",
        "executables": ["zaproxy", "zap.sh", "zap.bat", "ZAP.exe"],
        "version_args": ["-version"],
        "purpose": "Web proxy/scanner for lab use",
        "category": "Web Security",
        "modules": ["web_security"],
        "integration": "DETECTION_AND_LAUNCH_ONLY",
        "docs": "https://www.zaproxy.org/docs/",
        "install": {
            "Linux": "Official packages/distributions: https://www.zaproxy.org/download/",
            "Windows": "Official installer: https://www.zaproxy.org/download/",
            "Darwin": "Official installer: https://www.zaproxy.org/download/",
        },
    },
    "metasploit": {
        "display": "Metasploit Framework",
        "executables": ["msfconsole"],
        "version_args": ["--version"],
        "purpose": "Authorized lab tool",
        "category": "Lab Frameworks",
        "modules": ["lab"],
        "integration": "DETECTION_AND_LAUNCH_ONLY",
        "docs": "https://docs.metasploit.com/",
        "install": {
            "Linux": "Follow the official documentation for your distribution: https://docs.metasploit.com/docs/using-metasploit/getting-started/nightly-installers.html",
            "Windows": "Rapid7 provides official installers, but LupoHack integration on Windows is not verified: https://docs.rapid7.com/metasploit/installing-the-metasploit-framework/",
            "Darwin": "Rapid7 provides official installers, but LupoHack integration on macOS is not verified: https://docs.rapid7.com/metasploit/installing-the-metasploit-framework/",
        },
    },
    "git": {
        "display": "Git",
        "executables": ["git"],
        "version_args": ["--version"],
        "purpose": "Version control",
        "category": "Development Utilities",
        "modules": [],
        "integration": "DETECTION_ONLY",
        "docs": "https://git-scm.com/docs",
        "install": {
            "Linux": "Use your distribution’s official package manager.",
            "Windows": "Official installer: https://git-scm.com/download/win",
        },
    },
}


def _platform_key() -> str:
    if platform.system() == "Windows":
        return "Windows"
    if platform.system() != "Linux":
        return platform.system()
    try:
        with open("/etc/os-release", encoding="utf-8") as release_file:
            text = release_file.read().lower()
        if any(x in text for x in ("kali", "debian", "ubuntu")):
            return "Linux-debian"
        if any(x in text for x in ("fedora", "rhel", "centos")):
            return "Linux-fedora"
        if "arch" in text:
            return "Linux-arch"
    except OSError:
        pass
    return "Linux"


def inspect_tool(name: str) -> dict:
    key = name.lower()
    if key not in CATALOG:
        raise ValueError(f"Unknown tool: {name}")
    item = CATALOG[key]
    path = next((shutil.which(x) for x in item["executables"] if shutil.which(x)), None)
    version = None
    version_check_status = "NOT_AVAILABLE"
    version_check_error = None
    status = "MISSING"
    if path:
        status = "AVAILABLE"
        if key == "zap" and path.lower().endswith("zap.exe"):
            version_check_status = "UNSUPPORTED_EXECUTABLE"
        else:
            result = run_process([path, *item["version_args"]], timeout=5, max_output_bytes=4096)
            raw = (result.stdout or result.stderr).strip().splitlines()
            if result.status == "SUCCESS" and result.returncode == 0 and raw:
                version = raw[0][:300]
                version_check_status = "VERIFIED"
            else:
                version_check_status = "FAILED"
                version_check_error = (
                    result.error or result.stderr[:1000] or "Version command returned no output."
                )
    os_name = platform.system()
    supported = {
        "sherlock": ("Linux", "Windows", "Darwin"),
        "zap": ("Linux", "Windows", "Darwin"),
        "metasploit": ("Linux", "Windows", "Darwin"),
        "git": ("Windows", "Linux", "Darwin"),
    }[key]
    return {
        "id": key,
        "name": item["display"],
        "category": item["category"],
        "executable": path,
        "status": status,
        "version": version,
        "version_check_status": version_check_status,
        "version_check_error": version_check_error,
        "integration": item["integration"],
        "modules": item["modules"],
        "supported_os_expected": list(supported),
        "current_os": os_name,
        "platform_support_status": "EXPECTED_NOT_VERIFIED",
        "documentation": item["docs"],
        "installation_instructions": item["install"].get(
            _platform_key(), item["install"].get("Linux", "See the official documentation.")
        ),
        "limitations": "Finding an executable on PATH does not verify its authenticity or compatibility.",
    }


def check_python_dependency(name: str = "dnspython") -> dict:
    try:
        version = importlib.metadata.version(name)
        status = "AVAILABLE"
    except importlib.metadata.PackageNotFoundError:
        version = None
        status = "MISSING"
    return {
        "id": name,
        "name": name,
        "category": "Python runtime dependency for DNS",
        "executable": None,
        "status": status,
        "version": version,
        "integration": "CORE_REQUIRED",
        "modules": ["osint.dns"],
        "supported_os_expected": ["Windows", "Linux", "Darwin"],
        "platform_support_status": "EXPECTED_NOT_VERIFIED",
        "current_os": platform.system(),
        "documentation": "https://www.dnspython.org/",
        "installation_instructions": "Installed automatically by `python -m pip install -e .`; this is not a system tool.",
        "limitations": "Status of the Python distribution installed in the active environment.",
    }


def check_all() -> list[dict]:
    return [check_python_dependency(), *[inspect_tool(k) for k in CATALOG]]


def tool_inventory(
    *,
    query: str = "",
    category: str = "",
    status: str = "all",
    page: int = 1,
    page_size: int = 8,
) -> dict:
    """Return a fast presence-only inventory; never runs external tools."""
    if type(page) is not int or type(page_size) is not int:
        raise TypeError("Page and page_size must be integers.")
    if page < 1 or page_size < 1 or page_size > 50:
        raise ValueError("Page must be positive and page_size must be between 1 and 50.")
    if not isinstance(status, str):
        raise TypeError("Status must be a string: all, available, or missing.")
    normalized_status = status.strip().lower()
    if normalized_status not in {"all", "available", "missing"}:
        raise ValueError("Status must be all, available, or missing.")

    rows = []
    for key, item in CATALOG.items():
        executable = next(
            (path for name in item["executables"] if (path := shutil.which(name))), None
        )
        rows.append(
            {
                "id": key,
                "name": item["display"],
                "category": item["category"],
                "purpose": item["purpose"],
                "status": "AVAILABLE_ON_PATH" if executable else "MISSING",
                "executable": executable,
                "detection_source": "PATH lookup",
                "version_checked": False,
                "configuration_verified": False,
            }
        )

    query = query.strip().casefold()
    category_key = category.strip().casefold()
    filtered = [
        row
        for row in rows
        if (not query or query in " ".join(str(value) for value in row.values()).casefold())
        and (not category_key or row["category"].casefold() == category_key)
        and (
            normalized_status == "all"
            or (normalized_status == "available" and row["status"] == "AVAILABLE_ON_PATH")
            or (normalized_status == "missing" and row["status"] == "MISSING")
        )
    ]
    total = len(filtered)
    pages = max(1, (total + page_size - 1) // page_size)
    if page > pages:
        raise ValueError(f"Page must be between 1 and {pages} for these filters.")
    start = (page - 1) * page_size
    detected_categories = sorted(
        {row["category"] for row in rows if row["status"] == "AVAILABLE_ON_PATH"}
    )
    return {
        "summary": {
            "external_tools_total": len(rows),
            "available_on_path": sum(row["status"] == "AVAILABLE_ON_PATH" for row in rows),
            "missing_from_path": sum(row["status"] == "MISSING" for row in rows),
            "categories_with_available_tools": detected_categories,
        },
        "filters": {"query": query, "category": category, "status": normalized_status},
        "page": page,
        "page_size": page_size,
        "total_matching": total,
        "total_pages": pages,
        "items": filtered[start : start + page_size],
        "limitations": [
            "Presence detection only; it does not establish executability, version, configuration, or readiness.",
            "No external command was run to produce this inventory.",
        ],
    }


def installation_plan(name: str) -> dict:
    item = inspect_tool(name)
    if item["status"] == "AVAILABLE":
        if item["version_check_status"] != "VERIFIED":
            return {
                "status": "ALREADY_DETECTED_NOT_VERIFIED",
                "tool": item,
                "message": "Executable detected on PATH, but its version could not be verified; it will not be reinstalled automatically.",
            }
        return {
            "status": "ALREADY_INSTALLED",
            "tool": item,
            "message": "Tool already detected; it will not be reinstalled.",
        }
    if name.lower() == "sherlock" and shutil.which("pipx"):
        return {
            "status": "INSTALLER_AVAILABLE",
            "tool": item,
            "argv": [shutil.which("pipx"), "install", "sherlock-project"],
            "privileges": "Installs into the user’s isolated pipx environment; network access may be required.",
            "disk_space": "Not estimated; varies with Python dependencies.",
            "system_changes": "Creates an isolated pipx environment and installs Sherlock from the configured Python package index.",
            "instructions": "Verify the package source and also consult the project’s official documentation.",
        }
    return {
        "status": "MANUAL_INSTALL",
        "tool": item,
        "instructions": item["installation_instructions"],
        "privileges": "Varies by installation; consult the official source.",
        "system_changes": "LupoHack will make no changes to this system/platform.",
    }


def install_selected(name: str, *, confirmed: bool) -> dict:
    plan = installation_plan(name)
    if plan["status"] in ("ALREADY_INSTALLED", "ALREADY_DETECTED_NOT_VERIFIED"):
        return plan
    if not confirmed:
        return {
            **plan,
            "status": "CANCELLED",
            "message": "Installation not started; explicit confirmation is required.",
        }
    if plan["status"] != "INSTALLER_AVAILABLE":
        return {
            **plan,
            "status": "MANUAL_INSTALL",
            "message": "Automatic installation is unavailable; follow the official instructions.",
        }
    result = run_process(plan["argv"], timeout=600, max_output_bytes=100_000)
    if result.status != "SUCCESS":
        return {
            **plan,
            "status": result.status,
            "returncode": result.returncode,
            "stderr": result.stderr[-4000:],
            "message": result.error or "Installer exited with an error.",
        }
    verified = inspect_tool(name)
    return {
        **plan,
        "status": "INSTALLED_AND_VERIFIED"
        if verified["status"] == "AVAILABLE" and verified["version_check_status"] == "VERIFIED"
        else "INSTALLED_BUT_NOT_VERIFIED",
        "verification": verified,
        "returncode": result.returncode,
    }
