import pytest

from app.config import get_settings


@pytest.fixture(autouse=True)
def fresh_settings():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_valores_por_defecto(monkeypatch):
    for name in ("BACKEND", "APP_VERSION", "LOG_LEVEL", "PORT"):
        monkeypatch.delenv(name, raising=False)

    settings = get_settings()

    assert settings.backend == "docker"
    assert settings.app_version == "dev"
    assert settings.port == 8000


def test_lee_variables_de_entorno(monkeypatch):
    monkeypatch.setenv("BACKEND", "Simulator")
    monkeypatch.setenv("PORT", "10000")
    monkeypatch.setenv("LOG_LEVEL", "debug")

    settings = get_settings()

    assert settings.backend == "simulator"
    assert settings.port == 10000
    assert settings.log_level == "DEBUG"


def test_backend_invalido_falla_al_arrancar(monkeypatch):
    monkeypatch.setenv("BACKEND", "kubernetes")

    with pytest.raises(ValueError, match="BACKEND"):
        get_settings()
