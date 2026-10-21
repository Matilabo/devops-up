import urllib.error
from unittest.mock import MagicMock

from app import healthcheck


def test_sale_con_cero_si_la_api_responde(monkeypatch):
    response = MagicMock(status=200)
    response.__enter__.return_value = response
    monkeypatch.setattr(healthcheck.urllib.request, "urlopen", lambda url, timeout: response)

    assert healthcheck.main() == 0


def test_sale_con_uno_si_la_api_no_responde(monkeypatch):
    def refuse(url, timeout):
        raise urllib.error.URLError("Connection refused")

    monkeypatch.setattr(healthcheck.urllib.request, "urlopen", refuse)

    assert healthcheck.main() == 1
