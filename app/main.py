"""Aplicación FastAPI: rutas HTTP de la API de contenedores."""

from fastapi import FastAPI

from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="devops-up",
    description=(
        "API REST que se conecta al demonio de Docker para listar contenedores, "
        "consultar su consumo de CPU y memoria, y reiniciarlos o detenerlos."
    ),
    version=settings.app_version,
)


@app.get("/health", tags=["salud"], summary="Estado de la API")
def health() -> dict:
    return {"status": "ok", "version": settings.app_version}
