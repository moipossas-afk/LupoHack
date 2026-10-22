"""Catalog and safe management of optional external tools."""

from __future__ import annotations

import importlib.metadata
import platform
import shutil

from lupohack.integrations.process import run_process

CATALOG = {
    "nmap": {
        "display": "Nmap",
        "executables": ["nmap"],
        "version_args": ["--version"],
        "purpose": "Controlled discovery of authorized TCP services",
        "modules": ["network"],
        "integration": "IMPLEMENTED_LIMITED",
        "docs": "https://nmap.org/book/man.html",
        "install": {
            "Linux-debian": "sudo apt-get install nmap",
            "Linux-fedora": "sudo dnf install nmap",
            "Linux-arch": "sudo pacman -S nmap",
            "Windows": "Official installer: https://nmap.org/download.html",
            "Darwin": "Official downloads: https://nmap.org/download.html",
        },
    },
    "sherlock": {
        "display": "Sherlock",
        "executables": ["sherlock"],
        "version_args": ["--version"],
        "purpose": "Search for usernames on public websites",
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
        "nmap": ("Linux", "Windows", "Darwin"),
        "sherlock": ("Linux", "Windows", "Darwin"),
        "zap": ("Linux", "Windows", "Darwin"),
        "metasploit": ("Linux", "Windows", "Darwin"),
        "git": ("Windows", "Linux", "Darwin"),
    }[key]
    return {
        "id": key,
        "name": item["display"],
        "category": item["purpose"],
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
    if name.lower() == "nmap" and platform.system() == "Linux":
        key = _platform_key()
        commands = {
            "Linux-debian": ["sudo", "apt-get", "install", "nmap"],
            "Linux-fedora": ["sudo", "dnf", "install", "nmap"],
            "Linux-arch": ["sudo", "pacman", "-S", "--needed", "nmap"],
        }
        cmd = commands.get(key)
        if cmd and all(shutil.which(program) for program in cmd[:2]):
            return {
                "status": "INSTALLER_AVAILABLE",
                "tool": item,
                "argv": cmd,
                "privileges": "sudo/admin",
                "disk_space": "Not estimated; depends on the package manager and system dependencies.",
                "system_changes": "Installs the Nmap system package and package-manager dependencies.",
                "instructions": "After explicit confirmation, run the displayed command. LupoHack then checks the executable and version.",
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
