"""LupoHack CLI; direct commands and the menu share the same services."""

from __future__ import annotations

import argparse
import json
import sys

from lupohack import __version__
from lupohack.config import config_path, load_config, set_config_value
from lupohack.core.export import export_result
from lupohack.core.results import Result
from lupohack.core.store import clear_history, data_dir, history, save_result
from lupohack.core.validation import validate_ip_or_host, validate_port
from lupohack.diagnostics import diagnostics
from lupohack.integrations.lab_tools import launch_tool
from lupohack.integrations.sherlock import search_username
from lupohack.integrations.tool_manager import (
    CATALOG,
    check_all,
    inspect_tool,
    install_selected,
    installation_plan,
)
from lupohack.modules.files import compare_files, file_info
from lupohack.modules.network import dns_lookup, tcp_check
from lupohack.modules.osint import dns_records, rdap_lookup
from lupohack.modules.web import inspect_url


def _emit(obj, output=None):
    if isinstance(obj, (dict, list, tuple)):
        print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))
    else:
        print(obj)
    if output:
        row = (
            obj
            if isinstance(obj, dict) and "module" in obj
            else {
                "module": "cli",
                "operation": "result",
                "status": "SUCCESS",
                "summary": "Operation result",
                "findings": [obj] if isinstance(obj, dict) else [],
                "metadata": obj if isinstance(obj, dict) else {"text": str(obj)},
            }
        )
        export_result(row, output)
        print(f"Exported: {output}")


def _save(module, operation, target, data, output=None):
    raw_status = data.get("status")
    status = (
        raw_status
        if raw_status in {"SUCCESS", "PARTIAL", "FAILED", "CANCELLED", "SKIPPED"}
        else "SKIPPED"
        if raw_status == "UNAVAILABLE"
        else "SUCCESS"
    )
    summary = {
        "FAILED": f"Operation {operation} failed.",
        "CANCELLED": f"Operation {operation} was cancelled.",
        "PARTIAL": f"Operation {operation} completed with partial results.",
        "SKIPPED": f"Operation {operation} was skipped because the required integration is unavailable.",
    }.get(status, f"Operation {operation} completed.")
    r = Result(
        module=module,
        operation=operation,
        target=target,
        summary=summary,
        findings=[data],
        status=status,
    )
    path = save_result(r)
    _emit(r.to_dict(), output)
    print(f"Local history: {path}")


def _validate_network_scope(target):
    host = validate_ip_or_host(target)
    allowed = load_config()["allowed_targets"]
    if allowed and host not in allowed:
        raise ValueError(
            "Target is not in the configured allowed_targets list; operation not started."
        )
    return host


def build_parser():
    p = argparse.ArgumentParser(
        prog="lupohack",
        description="LupoHack — local defensive security toolkit",
        epilog="Use only on assets and data you are authorized to access.",
    )
    p.add_argument("--version", action="version", version=f"LupoHack {__version__}")
    sub = p.add_subparsers(dest="command")
    sub.add_parser("diagnostics", help="Diagnose the environment and dependencies")
    t = sub.add_parser("tools", help="Unified external tool manager")
    tsub = t.add_subparsers(dest="tool_action")
    tsub.add_parser("check", help="Check all dependencies")
    tq = tsub.add_parser("show", help="Inspect a dependency")
    tq.add_argument("name", choices=list(CATALOG))
    tq = tsub.add_parser("install", help="Show instructions or install with explicit confirmation")
    tq.add_argument("name", choices=list(CATALOG))
    tq.add_argument(
        "--execute",
        action="store_true",
        help="Request confirmation and run only a supported installer",
    )
    tq = tsub.add_parser("launch", help="Launch ZAP or Metasploit locally after confirmation")
    tq.add_argument("name", choices=["zap", "metasploit"])
    tq = tsub.add_parser("setup", help="Show the Core or Full Toolkit setup plan")
    tq.add_argument(
        "--full", action="store_true", help="Include setup plans for optional external tools"
    )
    o = sub.add_parser("osint", help="Public DNS and RDAP lookups")
    osub = o.add_subparsers(dest="action", required=True)
    for act in ("dns", "rdap", "username"):
        q = osub.add_parser(act)
        q.add_argument("value", help="Domain for DNS/RDAP or username for Sherlock")
        q.add_argument("-o", "--output")
    n = sub.add_parser("network", help="Basic network diagnostics")
    nsub = n.add_subparsers(dest="action", required=True)
    q = nsub.add_parser("dns")
    q.add_argument("host")
    q.add_argument("-o", "--output")
    q = nsub.add_parser("tcp")
    q.add_argument("host")
    q.add_argument("port", type=int)
    q.add_argument(
        "--authorized",
        action="store_true",
        help="Confirm that you are authorized to test the target",
    )
    q.add_argument("-o", "--output")
    w = sub.add_parser("web", help="Inspect HTTP(S) headers on public destinations")
    w.add_argument("url")
    w.add_argument("--authorized", action="store_true")
    w.add_argument("-o", "--output")
    f = sub.add_parser("files", help="Local file hashes and metadata")
    fsub = f.add_subparsers(dest="action", required=True)
    q = fsub.add_parser("hash")
    q.add_argument("path")
    q.add_argument("--algorithm", choices=["sha256", "sha512", "sha1", "md5"], default="sha256")
    q.add_argument("-o", "--output")
    q = fsub.add_parser("compare")
    q.add_argument("first")
    q.add_argument("second")
    q.add_argument("--algorithm", choices=["sha256", "sha512", "sha1", "md5"], default="sha256")
    q.add_argument("-o", "--output")
    r = sub.add_parser("reports", help="View or clear history and export results")
    rsub = r.add_subparsers(dest="action", required=True)
    q = rsub.add_parser("list")
    q.add_argument("--module")
    q = rsub.add_parser("show")
    q.add_argument("id")
    rsub.add_parser("clear")
    q = rsub.add_parser("export")
    q.add_argument("id")
    q.add_argument("path")
    c = sub.add_parser("config", help="Validated local configuration")
    csub = c.add_subparsers(dest="config_action")
    csub.add_parser("show", help="Show the effective configuration")
    cq = csub.add_parser("set", help="Update a validated field; value must be JSON")
    cq.add_argument("key")
    cq.add_argument("value")
    csub.add_parser("path", help="Show the configuration path")
    return p


def run(args):
    if args.command == "diagnostics":
        _emit(diagnostics())
    elif args.command == "tools":
        action = args.tool_action
        if action in (None, "check"):
            _emit(check_all())
        elif action == "show":
            _emit(inspect_tool(args.name))
        elif action == "install":
            plan = installation_plan(args.name)
            if args.execute and plan["status"] == "INSTALLER_AVAILABLE":
                print(json.dumps(plan, ensure_ascii=False, indent=2))
                phrase = f"INSTALL {args.name}"
                confirmed = (
                    input(
                        f"This installation may modify your system and requires {plan['privileges']}. Type {phrase} to confirm: "
                    ).strip()
                    == phrase
                )
                _emit(install_selected(args.name, confirmed=confirmed))
            else:
                _emit(plan)
        elif action == "setup":
            if args.full:
                _emit(
                    {
                        "profile": "Full Toolkit plan (no installation started)",
                        "core": {
                            "command": "python -m pip install -e .",
                            "includes": "LupoHack and the dnspython dependency",
                        },
                        "optional_tools": [installation_plan(name) for name in CATALOG],
                    }
                )
            else:
                _emit(
                    {
                        "profile": "Core",
                        "command": "python -m pip install -e .",
                        "includes": "LupoHack and dnspython",
                        "external_tools": "Core setup does not install optional tools. Check current availability with `lupohack tools check`.",
                    }
                )
        elif action == "launch":
            info = inspect_tool(args.name)
            print(json.dumps(info, ensure_ascii=False, indent=2))
            phrase = f"OPEN {args.name}"
            confirmed = (
                input(
                    f"This only launches the local application; it does not run scans or exploits. Type {phrase}: "
                ).strip()
                == phrase
            )
            _emit(launch_tool(args.name, confirmed=confirmed))
    elif args.command == "config":
        action = args.config_action
        if action == "path":
            print(config_path())
        elif action == "set":
            _emit({"path": str(config_path()), "config": set_config_value(args.key, args.value)})
        else:
            _emit({"path": str(config_path()), "config": load_config()})
    elif args.command == "osint":
        if args.action == "dns":
            data = dns_records(args.value)
        elif args.action == "rdap":
            data = rdap_lookup(args.value)
        else:
            data = search_username(args.value)
        _save("osint", args.action, args.value, data, args.output)
    elif args.command == "network":
        if args.action == "dns":
            data = dns_lookup(args.host)
            _save("network", "dns", args.host, data, args.output)
        elif args.action == "tcp":
            if not args.authorized:
                raise ValueError(
                    "Operation cancelled. Use --authorized only if you have explicit authorization for this target."
                )
            host = _validate_network_scope(args.host)
            data = tcp_check(host, args.port)
            _save("network", "tcp", f"{host}:{args.port}", data, args.output)
    elif args.command == "web":
        if not args.authorized:
            raise ValueError(
                "Operation cancelled. Use --authorized only if you have explicit authorization."
            )
        data = inspect_url(args.url)
        _save("web_security", "inspect", args.url, data, args.output)
    elif args.command == "files":
        data = (
            file_info(args.path, (args.algorithm,))
            if args.action == "hash"
            else compare_files(args.first, args.second, args.algorithm)
        )
        _save(
            "file_analysis",
            args.action,
            args.path if args.action == "hash" else f"{args.first} <> {args.second}",
            data,
            args.output,
        )
    elif args.command == "reports":
        if args.action == "list":
            _emit(history(args.module))
        elif args.action == "clear":
            answer = (
                input(f"Delete all local history? ({data_dir()}/history) [y/N] ").strip().lower()
            )
            if answer == "y":
                print(f"Records deleted: {clear_history()}")
            else:
                print("Cancelled; history was preserved.")
        else:
            rows = history()
            row = next((x for x in rows if x.get("id") == args.id), None)
            if row is None:
                raise ValueError("Report not found.")
            if args.action == "show":
                _emit(row)
            else:
                export_result(row, args.path)
                print(f"Exported: {args.path}")
    else:
        return menu()
    return 0


def menu():
    while True:
        print(
            "\n   /\\_/\\       L U P O H A C K  /  V1.0.0\n"
            "  ( o.o )       Local defensive security toolkit\n"
            "   > ^ <\n"
            "╔══════════════════════════════════════════╗"
        )
        print(
            "[1] Dashboard and diagnostics\n[2] OSINT — DNS/RDAP\n[3] Network — authorized DNS/TCP\n[4] Web security — public inspection\n[5] File analysis\n[6] External tools\n[7] Authorized lab guide\n[8] Reports and history\n[9] Settings\n[0] Exit"
        )
        try:
            choice = input("\nSelect an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSession ended.")
            return 0
        try:
            if choice == "0":
                print("Goodbye.")
                return 0
            elif choice == "1":
                _emit(diagnostics())
            elif choice == "2":
                d = input("Domain/username: ").strip()
                act = input("[1] DNS [2] RDAP [3] Sherlock username search: ").strip()
                operation = {"1": "dns", "2": "rdap", "3": "username"}.get(act)
                if operation is None:
                    print("Invalid option.")
                else:
                    data = (
                        dns_records(d)
                        if operation == "dns"
                        else rdap_lookup(d)
                        if operation == "rdap"
                        else search_username(d)
                    )
                    _save("osint", operation, d, data)
            elif choice == "3":
                h = input("Host: ").strip()
                act = input("[1] DNS [2] TCP: ").strip()
                if act == "1":
                    _save("network", "dns", h, dns_lookup(h))
                elif act == "2":
                    h = _validate_network_scope(h)
                    port = validate_port(int(input("Port: ")))
                    confirm = input(f"Confirm you are authorized to test {h}:{port}? Type YES: ")
                    if confirm == "YES":
                        _save("network", "tcp", f"{h}:{port}", tcp_check(h, port))
                    else:
                        print("Cancelled; no connection was attempted.")
            elif choice == "4":
                u = input("URL: ").strip()
                confirm = input(
                    "Confirm that you are authorized to inspect this service. Type YES: "
                )
                if confirm == "YES":
                    _save("web_security", "inspect", u, inspect_url(u))
                else:
                    print("Cancelled.")
            elif choice == "5":
                path = input("File path: ").strip()
                _save("file_analysis", "hash", path, file_info(path))
            elif choice == "6":
                print(
                    "Tool Manager: [1] check all [2] inspect [3] install/guide [4] launch ZAP/Metasploit [5] Core/Full setup"
                )
                action = input("Action: ").strip()
                if action in ("1", ""):
                    _emit(check_all())
                elif action == "2":
                    name = input(f"Tool ({', '.join(CATALOG)}): ").strip().lower()
                    _emit(inspect_tool(name))
                elif action == "3":
                    name = input(f"Tool ({', '.join(CATALOG)}): ").strip().lower()
                    plan = installation_plan(name)
                    _emit(plan)
                    if plan["status"] == "INSTALLER_AVAILABLE":
                        phrase = f"INSTALL {name}"
                        confirmed = (
                            input(f"Confirm system changes by typing {phrase}: ").strip() == phrase
                        )
                        result = install_selected(name, confirmed=confirmed)
                        _emit(result)
                        if result.get("status") in (
                            "INSTALLED_AND_VERIFIED",
                            "INSTALLED_BUT_NOT_VERIFIED",
                        ):
                            _emit(inspect_tool(name))
                elif action == "4":
                    name = input("Tool [zap/metasploit]: ").strip().lower()
                    if name not in ("zap", "metasploit"):
                        print("Invalid tool. Choose zap or metasploit.")
                    else:
                        phrase = f"OPEN {name}"
                        confirmed = (
                            input(f"This only opens the local application. Type {phrase}: ").strip()
                            == phrase
                        )
                        _emit(launch_tool(name, confirmed=confirmed))
                elif action == "5":
                    profile = input("Setup [core/full]: ").strip().lower()
                    if profile == "full":
                        _emit(
                            {
                                "profile": "Full Toolkit plan",
                                "tools": [installation_plan(name) for name in CATALOG],
                            }
                        )
                    elif profile == "core":
                        _emit(
                            {
                                "profile": "Core",
                                "command": "python -m pip install -e .",
                                "optional_tools": "Not installed by Core setup.",
                            }
                        )
                    else:
                        print("Invalid setup profile. Choose core or full.")
                else:
                    print("Invalid action.")
            elif choice == "7":
                print(
                    "Use an isolated lab: an analysis VM and a deliberately vulnerable target VM on a host-only network with no Internet bridge. LupoHack V1 does not run exploits or launch Metasploit automatically. See docs/LABORATORY.md."
                )
            elif choice == "8":
                _emit(history())
            elif choice == "9":
                _emit({"path": str(config_path()), "config": load_config()})
            else:
                print("Invalid option. Choose 0–9.")
        except (ValueError, OSError, TimeoutError) as e:
            print(f"ERROR: {e}")
        input("\nPress Enter to continue...")


def main():
    parser = build_parser()
    try:
        return run(parser.parse_args())
    except KeyboardInterrupt:
        print("\nOperation cancelled by the user.")
        return 130
    except (ValueError, OSError, TimeoutError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
