"""Configuración de la API leída de variables de entorno."""

import os
from dataclasses import dataclass
from functools import lru_cache

BACKENDS = ("docker", "simulator")


@dataclass(frozen=True)
class Settings:
    backend: str
    app_version: str
    log_level: str
    host: str
    port: int


@lru_cache
def get_settings() -> Settings:
    backend = os.getenv("BACKEND", "docker").lower()
    if backend not in BACKENDS:
        raise ValueError(f"BACKEND debe ser uno de {BACKENDS}, no {backend!r}")

    return Settings(
        backend=backend,
        app_version=os.getenv("APP_VERSION", "dev"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
    )
