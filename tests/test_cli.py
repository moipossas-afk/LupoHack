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


def test_menu_rejects_invalid_tool_and_setup_profile(monkeypatch, capsys):
    from lupohack.cli import menu

    replies = iter(["6", "4", "invalid", "", "6", "5", "unknown", "", "0"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(replies))
    monkeypatch.setattr(
        "lupohack.cli.launch_tool", lambda *a, **k: pytest.fail("invalid tool was launched")
    )
    assert menu() == 0
    output = capsys.readouterr().out
    assert "Invalid tool" in output
    assert "Invalid setup profile" in output


def test_saved_result_summary_matches_failure_status(monkeypatch):
    from lupohack.cli import _save

    captured = []
    monkeypatch.setattr("lupohack.cli.save_result", lambda _result: "history.json")
    monkeypatch.setattr("lupohack.cli._emit", lambda result, _output=None: captured.append(result))
    _save("network", "tcp", "example.test:443", {"status": "FAILED"})
    assert captured[0]["status"] == "FAILED"
    assert captured[0]["summary"] == "Operation tcp failed."
