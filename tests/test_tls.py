import pytest

from lupohack.modules import tls


class FakeTLSSocket:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def getpeercert(self):
        return {
            "subject": ((("commonName", "lab.example"),),),
            "issuer": ((("commonName", "Test CA"),),),
            "subjectAltName": (("DNS", "lab.example"), ("IP Address", "192.0.2.5")),
            "notBefore": "Jan  1 00:00:00 2025 GMT",
            "notAfter": "Dec 31 23:59:59 2099 GMT",
        }

    def version(self):
        return "TLSv1.3"

    def cipher(self):
        return ("TLS_AES_256_GCM_SHA384", "TLSv1.3", 256)


class FakeContext:
    def __init__(self):
        self.server_name = None

    def wrap_socket(self, sock, server_hostname):
        self.server_name = server_hostname
        return FakeTLSSocket()


def test_inspect_tls_uses_hostname_verification_and_returns_peer_metadata(monkeypatch):
    context = FakeContext()
    monkeypatch.setattr(tls.ssl, "create_default_context", lambda: context)
    monkeypatch.setattr(tls.socket, "create_connection", lambda address, timeout: FakeTLSSocket())

    result = tls.inspect_tls("LAB.example", timeout=3)

    assert result["status"] == "VERIFIED"
    assert result["certificate_validation"] == "PASSED"
    assert result["host"] == "lab.example"
    assert result["tls_version"] == "TLSv1.3"
    assert "lab.example" in result["subject_alt_names"]
    assert result["expires_in_days"] > 0
    assert context.server_name == "lab.example"


def test_inspect_tls_turns_connection_errors_into_structured_failure(monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("simulated connection refusal")

    monkeypatch.setattr(tls.socket, "create_connection", fail)
    result = tls.inspect_tls("lab.example")
    assert result["status"] == "FAILED"
    assert "simulated connection refusal" in result["error"]


def test_inspect_tls_validates_target_port_and_timeout():
    with pytest.raises(ValueError, match="Invalid host"):
        tls.inspect_tls("bad/host")
    with pytest.raises(ValueError, match="Port must"):
        tls.inspect_tls("lab.example", 70000)
    with pytest.raises(ValueError, match="Timeout must"):
        tls.inspect_tls("lab.example", timeout=0)
