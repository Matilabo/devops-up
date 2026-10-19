"""Aplicación FastAPI: rutas HTTP de la API de contenedores."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI

from app.config import get_settings
from app.docker_service import DockerService
from app.schemas import ContainerSummary, ErrorResponse, Health

settings = get_settings()

app = FastAPI(
    title="devops-up",
    description=(
        "API REST que se conecta al demonio de Docker para listar contenedores, "
        "consultar su consumo de CPU y memoria, y reiniciarlos o detenerlos."
    ),
    version=settings.app_version,
)


@lru_cache
def get_service() -> DockerService:
    return DockerService()


Service = Annotated[DockerService, Depends(get_service)]

DOCKER_UNAVAILABLE = {503: {"model": ErrorResponse, "description": "Docker no disponible"}}


@app.get("/health", response_model=Health, tags=["salud"], summary="Estado de la API")
def health(service: Service):
    return {
        "status": "ok",
        "version": settings.app_version,
        "backend_available": service.ping(),
    }


@app.get(
    "/containers",
    response_model=list[ContainerSummary],
    responses=DOCKER_UNAVAILABLE,
    tags=["contenedores"],
    summary="Listar contenedores activos",
)
def list_containers(service: Service):
    return service.list_containers()
