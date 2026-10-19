from unittest.mock import MagicMock

import newrelic.agent

from app.__main__ import init_newrelic


def test_sin_license_key_no_inicia_new_relic(monkeypatch):
    monkeypatch.delenv("NEW_RELIC_LICENSE_KEY", raising=False)
    initialize = MagicMock()
    monkeypatch.setattr(newrelic.agent, "initialize", initialize)

    assert init_newrelic() is False
    initialize.assert_not_called()


def test_con_license_key_inicia_el_agente(monkeypatch):
    monkeypatch.setenv("NEW_RELIC_LICENSE_KEY", "clave-de-prueba")
    initialize = MagicMock()
    monkeypatch.setattr(newrelic.agent, "initialize", initialize)

    assert init_newrelic() is True
    initialize.assert_called_once_with()
