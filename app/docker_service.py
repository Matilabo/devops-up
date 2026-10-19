"""Acceso al demonio de Docker mediante el SDK oficial (`docker`)."""

from contextlib import contextmanager

import docker
import requests
from docker.errors import APIError, DockerException, NotFound

from app.errors import (
    ContainerNotFoundError,
    ContainerNotRunningError,
    ContainerOperationError,
    ContainerServiceError,
    DockerUnavailableError,
)
from app.metrics import cpu_percent, memory_usage


@contextmanager
def docker_errors(ref: str = ""):
    """Traduce las excepciones del SDK a errores propios de la API."""
    try:
        yield
    except NotFound as exc:
        raise ContainerNotFoundError(ref) from exc
    except APIError as exc:
        raise ContainerOperationError(exc.explanation or str(exc)) from exc
    except (DockerException, requests.exceptions.ConnectionError) as exc:
        raise DockerUnavailableError() from exc


class DockerService:
    """Operaciones sobre los contenedores del demonio de Docker local."""

    def __init__(self, client_factory=docker.from_env):
        self._client_factory = client_factory
        self._client = None

    @property
    def client(self):
        # El cliente se crea recién al primer uso: la API arranca aunque Docker esté caído.
        if self._client is None:
            with docker_errors():
                self._client = self._client_factory()
        return self._client

    def ping(self) -> bool:
        try:
            with docker_errors():
                return bool(self.client.ping())
        except ContainerServiceError:
            return False

    def list_containers(self) -> list[dict]:
        with docker_errors():
            containers = self.client.containers.list(ignore_removed=True)
        return [summary(container) for container in containers]

    def get_stats(self, ref: str) -> dict:
        with docker_errors(ref):
            container = self.client.containers.get(ref)
            if container.status != "running":
                raise ContainerNotRunningError(ref)
            stats = container.stats(stream=False)
        return {
            "id": container.short_id,
            "name": container.name,
            "cpu_percent": cpu_percent(stats),
            **memory_usage(stats),
        }


def summary(container) -> dict:
    return {
        "id": container.short_id,
        "name": container.name,
        "image": container.attrs.get("Config", {}).get("Image", ""),
        "status": container.status,
    }
