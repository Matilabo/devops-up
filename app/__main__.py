"""Arranca el servidor HTTP: `python -m app`."""

import os

from app.config import get_settings
from app.logging_config import build_log_config


def init_newrelic() -> bool:
    """Activa el agente de New Relic solo si hay license key (sin key la API corre igual)."""
    if not os.getenv("NEW_RELIC_LICENSE_KEY"):
        return False

    import newrelic.agent

    # Toma el resto de la configuración de variables NEW_RELIC_* (app name, logs, etc.).
    newrelic.agent.initialize()
    return True


def main() -> None:
    settings = get_settings()
    init_newrelic()

    # Se importa después de iniciar el agente para que pueda instrumentar el servidor.
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_config=build_log_config(settings.log_level),
        # El access log de uvicorn no es JSON: cada request lo loguea el middleware de la app.
        access_log=False,
    )


if __name__ == "__main__":
    main()
