import pytest

from lupohack.cli import _emit, build_parser


def test_help_parser():
    p = build_parser()
    assert p.prog == "lupohack"
    args = p.parse_args(["network", "tcp", "127.0.0.1", "443", "--authorized"])
    assert args.authorized


def test_direct_subcommand_help(capsys):
    p = build_parser()
    try:
        p.parse_args(["osint", "--help"])
    except SystemExit as e:
        assert e.code == 0
    assert "dns" in capsys.readouterr().out


def test_extended_commands_parse():
    p = build_parser()
    assert p.parse_args(["osint", "username", "public_user"]).action == "username"
    assert p.parse_args(["config", "set", "default_timeout_seconds", "10"]).value == "10"
    assert p.parse_args(["tools", "setup", "--full"]).full
    inventory = p.parse_args(["tools", "inventory", "--query", "git", "--page-size", "2"])
    assert inventory.query == "git" and inventory.page_size == 2
    tls = p.parse_args(["network", "tls", "lab.example", "--authorized"])
    assert tls.action == "tls" and tls.port == 443 and tls.authorized


def test_emit_serializes_tool_lists_as_json(capsys):
    _emit([{"id": "sherlock", "status": "MISSING"}])
    assert '"status": "MISSING"' in capsys.readouterr().out


def test_tcp_cli_enforces_configured_allowlist(monkeypatch, tmp_path):
    from lupohack.cli import run
    from lupohack.config import load_config, save_config

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    save_config({**load_config(), "allowed_targets": ["allowed.example"]})
    monkeypatch.setattr(
        "lupohack.cli.tcp_check", lambda *args, **kwargs: pytest.fail("out-of-scope target used")
    )
    args = build_parser().parse_args(["network", "tcp", "other.example", "443", "--authorized"])
    with pytest.raises(ValueError, match="allowed_targets"):
        run(args)


def test_tls_cli_requires_explicit_authorization(monkeypatch):
    from lupohack.cli import run

    monkeypatch.setattr(
        "lupohack.cli.inspect_tls",
        lambda *args, **kwargs: pytest.fail("TLS started without consent"),
    )
    args = build_parser().parse_args(["network", "tls", "lab.example"])
    with pytest.raises(ValueError, match="explicit authorization"):
        run(args)


def test_tls_cli_enforces_allowlist_and_saves_result(monkeypatch, tmp_path):
    from lupohack.cli import run
    from lupohack.config import load_config, save_config

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    save_config({**load_config(), "allowed_targets": ["lab.example"]})
    calls = []
    monkeypatch.setattr("lupohack.cli.inspect_tls", lambda host, port: {"status": "VERIFIED"})
    monkeypatch.setattr("lupohack.cli._save", lambda *args: calls.append(args))
    args = build_parser().parse_args(
        ["network", "tls", "LAB.example", "--authorized", "--port", "8443"]
    )
    run(args)
    assert calls == [("network", "tls", "lab.example:8443", {"status": "VERIFIED"}, None)]

    out_of_scope = build_parser().parse_args(["network", "tls", "other.example", "--authorized"])
    with pytest.raises(ValueError, match="allowed_targets"):
        run(out_of_scope)


def test_menu_has_ascii_responsive_branding():
    from lupohack.console import render_banner

    wide = render_banner(width=100, color=False)
    narrow = render_banner(width=40, color=False)
    assert "LUPOHACK" in wide and "LupoHack" in wide
    assert "LUPOHACK" in narrow and "Local defensive security toolkit" in narrow
    assert "\033[" not in wide + narrow


def test_menu_category_navigation_and_invalid_choice(monkeypatch, capsys):
    from lupohack.cli import menu

    replies = iter(["invalid", "5", "1", "", "", "", "N", "P", "", "B", "Q"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(replies))
    assert menu() == 0
    output = capsys.readouterr().out
    assert "Invalid category." in output
    assert "Tools & environment" in output
    assert "found on PATH" in output
    assert "Page 1 of 2" in output and "Page 2 of 2" in output
    assert "Goodbye." in output


def test_menu_context_help_main_menu_shortcut_and_lab_guide(monkeypatch, capsys):
    from lupohack.cli import menu

    replies = iter(["1", "H", "0", "5", "7", "", "Q"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(replies))
    assert menu() == 0
    output = capsys.readouterr().out
    assert "Configure allowed_targets" in output
    assert "host-only network" in output
    assert "Goodbye." in output


def test_menu_global_quit_from_inventory_search(monkeypatch, capsys):
    from lupohack.cli import menu

    replies = iter(["5", "1", "Q"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(replies))
    assert menu() == 0
    assert "Goodbye." in capsys.readouterr().out


def test_saved_result_summary_matches_failure_status(monkeypatch):
    from lupohack.cli import _save

    captured = []
    monkeypatch.setattr("lupohack.cli.save_result", lambda _result: "history.json")
    monkeypatch.setattr("lupohack.cli._emit", lambda result, _output=None: captured.append(result))
    _save("network", "tcp", "example.test:443", {"status": "FAILED"})
    assert captured[0]["status"] == "FAILED"
    assert captured[0]["summary"] == "Operation tcp failed."
