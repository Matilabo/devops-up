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
