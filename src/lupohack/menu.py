"""Categorized interactive console menu over the existing LupoHack services."""

from __future__ import annotations

import json
import shutil
import textwrap

from lupohack.config import config_path, load_config, set_config_value
from lupohack.console import render_banner
from lupohack.core.export import export_result
from lupohack.core.store import clear_history, data_dir, history
from lupohack.diagnostics import diagnostics
from lupohack.integrations.lab_tools import launch_tool
from lupohack.integrations.sherlock import search_username
from lupohack.integrations.tool_manager import (
    CATALOG,
    check_all,
    inspect_tool,
    install_selected,
    installation_plan,
    tool_inventory,
)
from lupohack.modules.files import compare_files, file_info
from lupohack.modules.network import dns_lookup, tcp_check
from lupohack.modules.osint import dns_records, rdap_lookup
from lupohack.modules.tls import inspect_tls
from lupohack.modules.web import inspect_url

CATEGORIES = {
    "1": (
        "Reconnaissance",
        "Public DNS records, RDAP registration data, and Sherlock username search.",
        (("1", "DNS records"), ("2", "RDAP lookup"), ("3", "Sherlock username search")),
    ),
    "2": (
        "Network diagnostics",
        "DNS resolution, one authorized TCP connection, or one verified TLS handshake.",
        (
            ("1", "DNS resolution"),
            ("2", "TCP connectivity check"),
            ("3", "TLS certificate inspection"),
        ),
    ),
    "3": (
        "Web security",
        "Non-invasive HTTP(S) response-header and redirect inspection.",
        (("1", "Inspect an HTTP(S) URL"),),
    ),
    "4": (
        "Files & forensics",
        "Local file metadata, cryptographic hashes, and file comparison.",
        (("1", "Hash and inspect file metadata"), ("2", "Compare two files")),
    ),
    "5": (
        "Tools & environment",
        "Presence-only inventory, explicit dependency checks, and optional tool management.",
        (
            ("1", "Browse tool inventory"),
            ("2", "Run detailed dependency checks"),
            ("3", "Inspect one optional tool"),
            ("4", "Show installation guide / install Sherlock"),
            ("5", "Launch local OWASP ZAP or Metasploit"),
            ("6", "Show setup plans"),
            ("7", "Authorized lab safety guide"),
        ),
    ),
    "6": (
        "Reports & history",
        "View locally stored operations, export a result, or clear local history.",
        (
            ("1", "List history"),
            ("2", "View a result by ID"),
            ("3", "Export a result"),
            ("4", "Clear history"),
        ),
    ),
    "7": (
        "Settings & help",
        "Inspect diagnostics or view and update validated local configuration.",
        (
            ("1", "Environment diagnostics"),
            ("2", "View configuration"),
            ("3", "Update a configuration field"),
            ("4", "Authorization and help"),
        ),
    ),
}


_MENU_HELP = (
    "Only the displayed operations exist in this release; external tools remain optional. "
    "B returns to the previous menu, 0 returns to the main menu, H shows contextual help, "
    "Q exits, and R refreshes a list where supported. Network connections require an explicit "
    "authorization confirmation. Configure allowed_targets to restrict network operations."
)


def _prompt(label: str) -> str:
    try:
        return input(label).strip()
    except (EOFError, KeyboardInterrupt):
        return "Q"


def _browse_inventory() -> bool:
    query = _prompt("Search text (Enter for all): ")
    if query.upper() == "Q":
        return True
    if query == "0":
        return False
    category = _prompt(
        "Category (Reconnaissance / Web Security / Lab Frameworks / Development Utilities; Enter for all): "
    )
    if category.upper() == "Q":
        return True
    if category == "0":
        return False
    status = _prompt("State [all/available/missing] (Enter=all): ").lower() or "all"
    if status.upper() == "Q":
        return True
    if status == "0":
        return False
    page = 1
    while True:
        result = tool_inventory(
            query=query, category=category, status=status, page=page, page_size=2
        )
        summary = result["summary"]
        print(
            f"\nExternal tools: {summary['external_tools_total']} total; "
            f"{summary['available_on_path']} found on PATH; {summary['missing_from_path']} not found."
        )
        categories = summary["categories_with_available_tools"]
        print("Categories with tools found: " + (", ".join(categories) if categories else "none"))
        print(
            f"Page {result['page']} of {result['total_pages']} ({result['total_matching']} matching)"
        )
        for row in result["items"]:
            location = row["executable"] or "not found on PATH"
            print(f"  {row['category']:<24} {row['name']:<20} {row['status']}: {location}")
        print(
            "Presence check only; executable version, configuration, and readiness are not verified."
        )
        if result["total_pages"] == 1:
            return False
        nav = _prompt("[N] next page [P] previous page [B] back: ").upper()
        if nav == "N" and page < result["total_pages"]:
            page += 1
        elif nav == "P" and page > 1:
            page -= 1
        else:
            return nav == "Q"
    return False


def _run_action(category: str, action: str, save, emit) -> None:
    if category == "1":
        value = _prompt("Domain or username: ")
        if action == "1":
            save("osint", "dns", value, dns_records(value))
        elif action == "2":
            save("osint", "rdap", value, rdap_lookup(value))
        else:
            save("osint", "username", value, search_username(value))
    elif category == "2":
        host = _prompt("Host: ")
        if action == "1":
            save("network", "dns", host, dns_lookup(host))
            return
        port = 443 if action == "3" else int(_prompt("Port: "))
        if not 1 <= port <= 65535:
            raise ValueError("Port must be between 1 and 65535.")
        from lupohack.cli import _validate_network_scope

        host = _validate_network_scope(host)
        confirmation = _prompt(f"Confirm authorization for {host}:{port}. Type YES: ")
        if confirmation != "YES":
            print("Cancelled; no network connection was attempted.")
            return
        data = tcp_check(host, port) if action == "2" else inspect_tls(host, port)
        operation = "tcp" if action == "2" else "tls"
        save("network", operation, f"{host}:{port}", data)
    elif category == "3":
        url = _prompt("URL: ")
        if _prompt("Confirm authorization to inspect this service. Type YES: ") == "YES":
            save("web_security", "inspect", url, inspect_url(url))
        else:
            print("Cancelled; no HTTP request was made.")
    elif category == "4":
        first = _prompt("File path: ")
        if action == "1":
            save("file_analysis", "hash", first, file_info(first))
        else:
            second = _prompt("Second file path: ")
            save("file_analysis", "compare", f"{first} <> {second}", compare_files(first, second))
    elif category == "5":
        if action == "1":
            return _browse_inventory()
        elif action == "2":
            emit(check_all())
        elif action == "3":
            name = _prompt(f"Tool ({', '.join(CATALOG)}): ").lower()
            emit(inspect_tool(name))
        elif action == "4":
            name = _prompt(
                "Tool name (Sherlock supports guided install; others show instructions): "
            ).lower()
            plan = installation_plan(name)
            emit(plan)
            if plan["status"] == "INSTALLER_AVAILABLE":
                phrase = f"INSTALL {name}"
                confirmed = _prompt(f"Confirm local system change by typing {phrase}: ") == phrase
                emit(install_selected(name, confirmed=confirmed))
        elif action == "5":
            name = _prompt("Local application [zap/metasploit]: ").lower()
            if name not in {"zap", "metasploit"}:
                raise ValueError("Choose zap or metasploit.")
            confirmed = (
                _prompt(f"Type OPEN {name} to launch the local application: ") == f"OPEN {name}"
            )
            emit(launch_tool(name, confirmed=confirmed))
        elif action == "6":
            profile = _prompt("Plan [core/full]: ").lower()
            if profile == "core":
                emit(
                    {
                        "profile": "Core",
                        "command": "python -m pip install -e .",
                        "includes": "LupoHack and dnspython",
                        "external_tools_installed": False,
                    }
                )
            elif profile == "full":
                emit(
                    {
                        "profile": "Full Toolkit plan; nothing installed",
                        "tools": [installation_plan(name) for name in CATALOG],
                    }
                )
            else:
                raise ValueError("Choose core or full.")
        elif action == "7":
            print(
                "Use an isolated lab: an analysis VM and a deliberately vulnerable target VM "
                "on a host-only network with no Internet bridge. LupoHack does not run exploits "
                "or launch Metasploit modules. See docs/LABORATORY.md."
            )
    elif category == "6":
        if action == "1":
            rows = history()
            emit(rows)
            print(f"{len(rows)} local history record(s).")
        elif action == "2":
            result_id = _prompt("Result ID: ")
            row = next((entry for entry in history() if entry.get("id") == result_id), None)
            if row is None:
                raise ValueError("Report not found.")
            emit(row)
        elif action == "3":
            result_id = _prompt("Result ID: ")
            row = next((entry for entry in history() if entry.get("id") == result_id), None)
            if row is None:
                raise ValueError("Report not found.")
            destination = _prompt("Export path (.json, .csv, or .txt): ")
            export_result(row, destination)
            print(f"Exported: {destination}")
        else:
            if _prompt(f"Delete local history in {data_dir()}/history? Type DELETE: ") == "DELETE":
                print(f"Records deleted: {clear_history()}")
            else:
                print("Cancelled; history was preserved.")
    elif category == "7":
        if action == "1":
            emit(diagnostics())
        elif action == "2":
            emit({"path": str(config_path()), "config": load_config()})
        elif action == "3":
            key = _prompt("Configuration key: ")
            raw_value = _prompt('Value as JSON (e.g. ["lab.example"]): ')
            emit({"path": str(config_path()), "config": set_config_value(key, raw_value)})
        else:
            print(_MENU_HELP)


def menu(save, emit) -> int:
    """Run the interactive category menu; ``save`` and ``emit`` reuse CLI services."""
    print(render_banner())
    terminal_width = shutil.get_terminal_size((80, 24)).columns
    while True:
        print("\nMAIN MENU")
        for key, (title, description, _options) in CATEGORIES.items():
            prefix = f"[{key}] {title}"
            if terminal_width < 68:
                print(prefix)
                for line in textwrap.wrap(description, width=max(20, terminal_width - 6)):
                    print("   " + line)
            else:
                print(f"{prefix:<30} {description}")
        print("[0] Exit")
        choice = _prompt("Select category [H help / Q quit]: ").upper()
        if choice in {"0", "Q"}:
            print("Goodbye.")
            return 0
        if choice == "H":
            print(_MENU_HELP)
            continue
        if choice not in CATEGORIES:
            print("Invalid category.")
            continue

        while True:
            title, description, options = CATEGORIES[choice]
            print(f"\n{title}\n{description}")
            for action, label in options:
                print(f"[{action}] {label}")
            print("[B] Back  [0] Main menu  [H] Help  [Q] Quit")
            action = _prompt("Select an option: ").upper()
            if action == "Q":
                print("Goodbye.")
                return 0
            if action in {"B", "0"}:
                break
            if action == "H":
                print(description + "\n" + _MENU_HELP)
                continue
            if action == "R" and choice == "5":
                try:
                    if _browse_inventory():
                        print("Goodbye.")
                        return 0
                except (ValueError, OSError, TimeoutError) as exc:
                    print(f"ERROR: {exc}")
                continue
            if action not in {key for key, _ in options}:
                print("Invalid option.")
                continue
            try:
                should_quit = _run_action(choice, action, save, emit)
            except (ValueError, OSError, TimeoutError, json.JSONDecodeError) as exc:
                print(f"ERROR: {exc}")
                should_quit = False
            if should_quit:
                print("Goodbye.")
                return 0
            navigation = _prompt(
                "Press Enter to continue, B back, 0 main menu, H help, or Q quit: "
            ).upper()
            if navigation == "Q":
                print("Goodbye.")
                return 0
            if navigation in {"B", "0"}:
                break
            if navigation == "H":
                print(description + "\n" + _MENU_HELP)
