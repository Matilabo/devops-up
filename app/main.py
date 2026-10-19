"""Aplicación FastAPI: rutas HTTP de la API de contenedores."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI, Path, Query

from app.config import get_settings
from app.docker_service import DockerService
from app.schemas import ActionResult, ContainerStats, ContainerSummary, ErrorResponse, Health

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
ContainerRef = Annotated[str, Path(description="ID (completo o corto) o nombre del contenedor")]
Timeout = Annotated[
    int, Query(ge=0, le=60, description="Segundos de espera antes de forzar el apagado")
]

DOCKER_UNAVAILABLE = {503: {"model": ErrorResponse, "description": "Docker no disponible"}}
CONTAINER_ERRORS = {
    404: {"model": ErrorResponse, "description": "El contenedor no existe"},
    **DOCKER_UNAVAILABLE,
}


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


@app.get(
    "/containers/{container_id}/stats",
    response_model=ContainerStats,
    responses={
        **CONTAINER_ERRORS,
        409: {"model": ErrorResponse, "description": "El contenedor no está en ejecución"},
    },
    tags=["contenedores"],
    summary="Consumo de CPU y memoria de un contenedor",
)
def container_stats(container_id: ContainerRef, service: Service):
    return service.get_stats(container_id)


@app.post(
    "/containers/{container_id}/restart",
    response_model=ActionResult,
    responses=CONTAINER_ERRORS,
    tags=["contenedores"],
    summary="Reiniciar un contenedor",
)
def restart_container(container_id: ContainerRef, service: Service, timeout: Timeout = 10):
    return service.restart(container_id, timeout)
