import pytest

from app.errors import (
    ContainerNotFoundError,
    ContainerNotRunningError,
    ContainerOperationError,
    DockerUnavailableError,
)


def test_health_responde_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["backend_available"] is True


def test_listar_contenedores(client, service):
    service.list_containers.return_value = [
        {"id": "abc123", "name": "web", "image": "nginx", "status": "running"}
    ]

    response = client.get("/containers")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "web"


def test_estadisticas_de_un_contenedor(client, service):
    service.get_stats.return_value = {
        "id": "abc123",
        "name": "web",
        "cpu_percent": 1.5,
        "memory_usage_mib": 10.0,
        "memory_limit_mib": 100.0,
        "memory_percent": 10.0,
    }

    response = client.get("/containers/web/stats")

    assert response.status_code == 200
    assert response.json()["cpu_percent"] == 1.5
    service.get_stats.assert_called_once_with("web")


def test_reiniciar_contenedor(client, service):
    service.restart.return_value = {
        "id": "abc123", "name": "web", "action": "restart", "status": "running"
    }

    response = client.post("/containers/web/restart?timeout=5")

    assert response.status_code == 200
    assert response.json()["status"] == "running"
    service.restart.assert_called_once_with("web", 5)


def test_detener_contenedor(client, service):
    service.stop.return_value = {
        "id": "abc123", "name": "web", "action": "stop", "status": "exited"
    }

    response = client.post("/containers/web/stop")

    assert response.status_code == 200
    assert response.json()["status"] == "exited"
    service.stop.assert_called_once_with("web", 10)


def test_timeout_fuera_de_rango_es_rechazado(client):
    response = client.post("/containers/web/restart?timeout=999")

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("error", "status_code"),
    [
        (ContainerNotFoundError("web"), 404),
        (ContainerNotRunningError("web"), 409),
        (ContainerOperationError("conflicto"), 502),
        (DockerUnavailableError(), 503),
    ],
)
def test_errores_del_servicio_se_traducen_a_http(client, service, error, status_code):
    service.get_stats.side_effect = error

    response = client.get("/containers/web/stats")

    assert response.status_code == status_code
    assert response.json() == {"detail": str(error)}


def test_health_informa_docker_caido(client, service):
    service.ping.return_value = False

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["backend_available"] is False
