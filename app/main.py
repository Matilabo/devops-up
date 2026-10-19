"""Aplicación FastAPI: rutas HTTP de la API de contenedores."""

import logging
import time
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI, Path, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import get_settings
from app.docker_service import DockerService
from app.errors import ContainerServiceError
from app.schemas import ActionResult, ContainerStats, ContainerSummary, ErrorResponse, Health
from app.simulator import SimulatorService

settings = get_settings()
logger = logging.getLogger("app.requests")

app = FastAPI(
    title="devops-up",
    description=(
        "API REST que se conecta al demonio de Docker para listar contenedores, "
        "consultar su consumo de CPU y memoria, y reiniciarlos o detenerlos."
    ),
    version=settings.app_version,
)


@lru_cache
def get_service() -> DockerService | SimulatorService:
    if settings.backend == "simulator":
        return SimulatorService()
    return DockerService()


Service = Annotated[DockerService | SimulatorService, Depends(get_service)]
ContainerRef = Annotated[str, Path(description="ID (completo o corto) o nombre del contenedor")]
Timeout = Annotated[
    int, Query(ge=0, le=60, description="Segundos de espera antes de forzar el apagado")
]

DOCKER_UNAVAILABLE = {503: {"model": ErrorResponse, "description": "Docker no disponible"}}
CONTAINER_ERRORS = {
    404: {"model": ErrorResponse, "description": "El contenedor no existe"},
    502: {"model": ErrorResponse, "description": "Docker rechazó la operación"},
    **DOCKER_UNAVAILABLE,
}


@app.exception_handler(ContainerServiceError)
async def container_service_error(request: Request, exc: ContainerServiceError):
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Loguea cada request con su status y duración (base de las golden signals)."""
    start = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        if status_code >= 500:
            level = logging.ERROR
        elif status_code >= 400:
            level = logging.WARNING
        else:
            level = logging.INFO
        logger.log(
            level,
            "%s %s -> %s",
            request.method,
            request.url.path,
            status_code,
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            },
        )


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=Health, tags=["salud"], summary="Estado de la API")
def health(service: Service):
    return {
        "status": "ok",
        "version": settings.app_version,
        "backend": settings.backend,
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


@app.post(
    "/containers/{container_id}/stop",
    response_model=ActionResult,
    responses=CONTAINER_ERRORS,
    tags=["contenedores"],
    summary="Detener un contenedor",
)
def stop_container(container_id: ContainerRef, service: Service, timeout: Timeout = 10):
    return service.stop(container_id, timeout)
