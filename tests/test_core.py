import json

import pytest

from lupohack.core.export import export_result
from lupohack.core.results import Result
from lupohack.core.validation import validate_domain, validate_network, validate_port, validate_url
from lupohack.diagnostics import diagnostics
from lupohack.modules.files import compare_files, file_info
from lupohack.modules.web import _public_destination


def test_validation():
    assert validate_domain("Example.COM.") == "example.com"
    with pytest.raises(ValueError):
        validate_url("file:///etc/passwd")
    with pytest.raises(ValueError):
        validate_url("https://user:pass@example.com")
    with pytest.raises(ValueError):
        validate_port(70000)
    assert validate_network("192.168.1.4/24") == "192.168.1.0/24"


def test_web_blocks_private():
    with pytest.raises(ValueError):
        _public_destination("http://127.0.0.1/")
    with pytest.raises(ValueError):
        _public_destination("http://192.168.0.1/")


def test_files(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.write_bytes(b"abc")
    b.write_bytes(b"abc")
    assert (
        file_info(str(a))["hashes"]["sha256"]
        == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
    assert compare_files(str(a), str(b))["match"]
    link = tmp_path / "link"
    link.symlink_to(a)
    with pytest.raises(ValueError):
        file_info(str(link))


def test_exports(tmp_path):
    r = Result(module="unit", operation="test", summary="ok")
    jp = export_result(r, tmp_path / "r.json")
    assert json.loads(jp.read_text())["module"] == "unit"
    cp = export_result(r, tmp_path / "r.csv")
    assert "module" in cp.read_text()
    tp = export_result(r, tmp_path / "r.txt")
    text = tp.read_text(encoding="utf-8")
    assert "Status:" in text and "Target:" in text and "Summary:" in text
    with pytest.raises(ValueError, match="Supported formats"):
        export_result(r, tmp_path / "r.bad")


def test_diagnostics():
    d = diagnostics()
    assert "python" in d and "tools" in d and d["data_writable"]
