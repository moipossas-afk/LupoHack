import sys

import pytest

from lupohack.config import ConfigError, config_path, load_config, save_config, set_config_value
from lupohack.integrations import nmap, sherlock, tool_manager
from lupohack.integrations.nmap import scan_authorized_host
from lupohack.integrations.process import run_process
from lupohack.integrations.sherlock import search_username


def test_run_process_reports_success_failure_missing_timeout_and_truncation():
    ok = run_process([sys.executable, "-c", "print('hello')"], timeout=5)
    assert ok.status == "SUCCESS" and "hello" in ok.stdout
    failed = run_process([sys.executable, "-c", "raise SystemExit(4)"], timeout=5)
    assert failed.status == "FAILED" and failed.returncode == 4
    missing = run_process(["lupohack-program-that-does-not-exist"])
    assert missing.status == "MISSING"
    slow = run_process([sys.executable, "-c", "import time; time.sleep(2)"], timeout=0.1)
    assert slow.status == "TIMEOUT"
    limited = run_process(
        [sys.executable, "-c", "print('x'*5000)"], timeout=5, max_output_bytes=100
    )
    assert len(limited.stdout) < 150 and "TRUNCATED" in limited.stdout


def test_process_cancellation_terminates_child(monkeypatch):
    import io

    class FakeProcess:
        stdout = io.BytesIO(b"")
        stderr = io.BytesIO(b"")
        returncode = None

        def __init__(self):
            self.wait_calls = 0
            self.terminated = False

        def wait(self, timeout=None):
            self.wait_calls += 1
            if self.wait_calls == 1:
                raise KeyboardInterrupt
            self.returncode = -15
            return -15

        def terminate(self):
            self.terminated = True

        def kill(self):
            raise AssertionError("terminate should suffice")

    child = FakeProcess()
    monkeypatch.setattr("lupohack.integrations.process.subprocess.Popen", lambda *a, **k: child)
    result = run_process(["fake-tool"])
    assert result.status == "CANCELLED" and child.terminated


def test_sherlock_validates_usernames_and_reports_unavailable_or_matches(monkeypatch):
    monkeypatch.setattr(sherlock, "executable", lambda: None)
    with pytest.raises(ValueError):
        search_username("invalid username!")
    with pytest.raises(ValueError):
        search_username("--help")
    assert search_username("valid_user")["status"] == "UNAVAILABLE"
    monkeypatch.setattr(sherlock, "executable", lambda: "/usr/bin/sherlock")
    monkeypatch.setattr(
        sherlock,
        "run_process",
        lambda *a, **k: type(
            "R",
            (),
            {
                "status": "SUCCESS",
                "returncode": 0,
                "stdout": "https://example.com/profile\n",
                "stderr": "",
                "error": None,
            },
        )(),
    )
    result = search_username("valid_user")
    assert result["outcome"] == "MATCHES_REPORTED"
    assert result["profiles"] == [
        {"url": "https://example.com/profile", "status": "FOUND_REPORTED_BY_TOOL"}
    ]


def test_nmap_scope_validation_and_mocked_xml(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr(nmap, "executable", lambda: "/usr/bin/nmap")
    xml = '<nmaprun><host><status state="up"/><address addr="198.51.100.4" addrtype="ipv4"/><ports><port protocol="tcp" port="443"><state state="open"/><service name="https"/></port></ports></host></nmaprun>'
    monkeypatch.setattr(
        nmap,
        "run_process",
        lambda *a, **k: type(
            "R",
            (),
            {"status": "SUCCESS", "returncode": 0, "stdout": xml, "stderr": "", "error": None},
        )(),
    )
    with pytest.raises(PermissionError):
        scan_authorized_host("example.test", authorized=False)
    result = scan_authorized_host("198.51.100.4", authorized=True)
    assert result["hosts"][0]["ports"][0]["state"] == "open"
    assert result["scope"].startswith("one host")


def test_nmap_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr(nmap, "executable", lambda: None)
    assert scan_authorized_host("example.test", authorized=True)["status"] == "UNAVAILABLE"


def test_nmap_respects_configured_allowlist(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    save_config({**load_config(), "allowed_targets": ["allowed.example"]})
    with pytest.raises(PermissionError, match="allowed_targets"):
        scan_authorized_host("other.example", authorized=True)


def test_config_validation_atomic_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    assert load_config()["language"] == "en"
    config = {**load_config(), "allowed_targets": ["EXAMPLE.test"], "default_timeout_seconds": 12}
    path = save_config(config)
    assert path == config_path()
    assert load_config()["allowed_targets"] == ["example.test"]
    assert set_config_value("history_enabled", "false")["history_enabled"] is False
    with pytest.raises(ConfigError):
        set_config_value("unknown", "1")
    with pytest.raises(ConfigError):
        save_config({**load_config(), "default_timeout_seconds": 99})
    save_config({**load_config(), "language": "pt"})
    assert load_config()["language"] == "en"


def test_tool_manager_missing_and_install_decisions(monkeypatch):
    monkeypatch.setattr(tool_manager.shutil, "which", lambda _name: None)
    assert tool_manager.inspect_tool("nmap")["status"] == "MISSING"
    assert tool_manager.installation_plan("nmap")["status"] in (
        "INSTALLER_AVAILABLE",
        "MANUAL_INSTALL",
    )
    assert tool_manager.install_selected("nmap", confirmed=False)["status"] == "CANCELLED"


def test_tool_manager_version_detection(monkeypatch):
    monkeypatch.setattr(
        tool_manager.shutil, "which", lambda name: "/usr/bin/nmap" if name == "nmap" else None
    )
    monkeypatch.setattr(
        tool_manager,
        "run_process",
        lambda *a, **k: type(
            "R",
            (),
            {"status": "SUCCESS", "stdout": "Nmap version 7.95", "stderr": "", "returncode": 0},
        )(),
    )
    result = tool_manager.inspect_tool("nmap")
    assert result["status"] == "AVAILABLE" and "7.95" in result["version"]
    assert result["version_check_status"] == "VERIFIED"
    assert result["platform_support_status"] == "EXPECTED_NOT_VERIFIED"


def test_tool_manager_does_not_claim_failed_version_check_is_verified(monkeypatch):
    monkeypatch.setattr(
        tool_manager.shutil, "which", lambda name: "/usr/bin/nmap" if name == "nmap" else None
    )
    monkeypatch.setattr(
        tool_manager,
        "run_process",
        lambda *a, **k: type(
            "R",
            (),
            {
                "status": "FAILED",
                "returncode": 1,
                "stdout": "",
                "stderr": "version probe failed",
                "error": None,
            },
        )(),
    )
    inspected = tool_manager.inspect_tool("nmap")
    assert inspected["status"] == "AVAILABLE"
    assert inspected["version"] is None
    assert inspected["version_check_status"] == "FAILED"
    assert tool_manager.installation_plan("nmap")["status"] == "ALREADY_DETECTED_NOT_VERIFIED"


def test_tool_manager_does_not_run_version_flags_on_zap_exe(monkeypatch):
    monkeypatch.setattr(
        tool_manager.shutil, "which", lambda name: "/apps/ZAP.exe" if name == "ZAP.exe" else None
    )
    monkeypatch.setattr(
        tool_manager,
        "run_process",
        lambda *a, **k: pytest.fail("ZAP.exe does not accept the desktop command-line options"),
    )
    result = tool_manager.inspect_tool("zap")
    assert result["status"] == "AVAILABLE"
    assert result["version_check_status"] == "UNSUPPORTED_EXECUTABLE"
    assert result["version"] is None


def test_metasploit_launch_is_confirmed_and_argument_free(monkeypatch):
    from lupohack.integrations import lab_tools

    monkeypatch.setattr(
        lab_tools,
        "inspect_tool",
        lambda _name: {"status": "AVAILABLE", "executable": "/usr/bin/msfconsole"},
    )
    calls = []
    monkeypatch.setattr(
        lab_tools.subprocess,
        "run",
        lambda argv, **kwargs: calls.append((argv, kwargs)) or type("P", (), {"returncode": 0})(),
    )
    assert lab_tools.launch_tool("metasploit", confirmed=False)["status"] == "CANCELLED"
    result = lab_tools.launch_tool("metasploit", confirmed=True)
    assert result["status"] == "EXITED"
    assert calls == [(["/usr/bin/msfconsole"], {"shell": False, "check": False})]
