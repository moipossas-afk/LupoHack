from lupohack.core.results import Result
from lupohack.core.store import clear_history, history, save_result
from lupohack.modules.network import dns_lookup
from lupohack.modules.osint import dns_records


def test_dns_invalid():
    import pytest

    with pytest.raises(ValueError):
        dns_lookup("not a host")


def test_dns_timeout_limit_message():
    import pytest

    with pytest.raises(ValueError, match="greater than 0 and at most 15 seconds"):
        dns_records("example.test", timeout=0)


def test_dns_all_record_types_without_network(monkeypatch):
    import dns.resolver

    class Item:
        preference = 10
        exchange = type("Name", (), {"to_text": lambda self: "mx.example."})()
        strings = (b"v=spf1 -all",)

        def to_text(self):
            return "203.0.113.10"

    class Answer:
        def __init__(self):
            self.rrset = [Item()]

        def __iter__(self):
            return iter(self.rrset)

    class FakeResolver:
        timeout = 1
        lifetime = 1

        def resolve(self, domain, record_type, **kwargs):
            return Answer()

    monkeypatch.setattr(dns.resolver, "Resolver", FakeResolver)
    result = dns_records("example.test")
    assert set(result["records"]) == {"A", "AAAA", "MX", "NS", "TXT", "CNAME"}
    assert result["records"]["MX"]["values"][0] == {"priority": 10, "exchange": "mx.example."}
    assert result["records"]["TXT"]["values"] == ["v=spf1 -all"]


def test_dns_timeout_state(monkeypatch):
    import dns.exception
    import dns.resolver

    class FakeResolver:
        timeout = 1
        lifetime = 1

        def resolve(self, *args, **kwargs):
            raise dns.exception.Timeout

    monkeypatch.setattr(dns.resolver, "Resolver", FakeResolver)
    result = dns_records("example.test", timeout=1)
    assert all(record["status"] == "TIMEOUT" for record in result["records"].values())
    assert result["status"] == "FAILED"


def test_history_roundtrip(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    r = Result(module="test", operation="roundtrip")
    save_result(r)
    assert history()[0]["id"] == r.id
    assert clear_history() == 1
    assert not history()


def test_rdap_network_error_is_structured(monkeypatch):
    import urllib.error
    import urllib.request

    from lupohack.modules.osint import rdap_lookup

    def fail(*args, **kwargs):
        raise urllib.error.URLError("mock offline")

    monkeypatch.setattr(urllib.request, "urlopen", fail)
    result = rdap_lookup("example.test")
    assert result["status"] == "FAILED"
    assert "mock offline" in result["error"]
