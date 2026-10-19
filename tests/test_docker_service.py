from unittest.mock import MagicMock

import pytest
import requests
from docker.errors import APIError, DockerException, NotFound

from app.docker_service import DockerService
from app.errors import (
    ContainerNotFoundError,
    ContainerNotRunningError,
    ContainerOperationError,
    DockerUnavailableError,
)
from app.metrics import MIB


def make_container(status="running"):
    container = MagicMock()
    container.short_id = "abc123def456"
    container.name = "web"
    container.status = status
    container.attrs = {"Config": {"Image": "nginx:1.30.6-alpine"}}
    return container


@pytest.fixture
def docker_client():
    return MagicMock()


@pytest.fixture
def service(docker_client):
    return DockerService(client_factory=lambda: docker_client)


def test_lista_contenedores_con_datos_basicos(service, docker_client):
    docker_client.containers.list.return_value = [make_container()]

    assert service.list_containers() == [
        {
            "id": "abc123def456",
            "name": "web",
            "image": "nginx:1.30.6-alpine",
            "status": "running",
        }
    ]
    docker_client.containers.list.assert_called_once_with(ignore_removed=True)


def test_estadisticas_calculan_cpu_y_memoria(service, docker_client):
    container = make_container()
    container.stats.return_value = {
        "cpu_stats": {
            "cpu_usage": {"total_usage": 300},
            "system_cpu_usage": 2000,
            "online_cpus": 1,
        },
        "precpu_stats": {"cpu_usage": {"total_usage": 100}, "system_cpu_usage": 1000},
        "memory_stats": {"usage": 64 * MIB, "limit": 512 * MIB, "stats": {}},
    }
    docker_client.containers.get.return_value = container

    stats = service.get_stats("web")

    assert stats["cpu_percent"] == 20.0
    assert stats["memory_usage_mib"] == 64.0
    assert stats["memory_percent"] == 12.5
    container.stats.assert_called_once_with(stream=False)


def test_estadisticas_de_contenedor_detenido(service, docker_client):
    container = make_container(status="exited")
    docker_client.containers.get.return_value = container

    with pytest.raises(ContainerNotRunningError):
        service.get_stats("web")
    container.stats.assert_not_called()


def test_reiniciar_recarga_el_estado(service, docker_client):
    container = make_container()
    docker_client.containers.get.return_value = container

    result = service.restart("web", timeout=3)

    container.restart.assert_called_once_with(timeout=3)
    container.reload.assert_called_once()
    assert result == {"id": "abc123def456", "name": "web", "action": "restart", "status": "running"}


def test_detener_contenedor(service, docker_client):
    container = make_container(status="exited")
    docker_client.containers.get.return_value = container

    result = service.stop("web")

    container.stop.assert_called_once_with(timeout=10)
    assert result["status"] == "exited"


def test_contenedor_inexistente(service, docker_client):
    docker_client.containers.get.side_effect = NotFound("No such container")

    with pytest.raises(ContainerNotFoundError):
        service.restart("nope")


def test_docker_rechaza_la_operacion(service, docker_client):
    container = make_container()
    container.stop.side_effect = APIError("409 Conflict", explanation="container is paused")
    docker_client.containers.get.return_value = container

    with pytest.raises(ContainerOperationError, match="container is paused"):
        service.stop("web")


def test_conexion_perdida_con_docker(service, docker_client):
    docker_client.containers.list.side_effect = requests.exceptions.ConnectionError()

    with pytest.raises(DockerUnavailableError):
        service.list_containers()


def test_docker_caido_al_crear_el_cliente():
    def broken_factory():
        raise DockerException("Error while fetching server API version")

    service = DockerService(client_factory=broken_factory)

    assert service.ping() is False
    with pytest.raises(DockerUnavailableError):
        service.list_containers()
