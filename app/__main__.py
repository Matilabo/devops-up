"""Arranca el servidor HTTP: `python -m app`."""

import uvicorn

from app.config import get_settings
from app.logging_config import build_log_config


def main() -> None:
    settings = get_settings()
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
