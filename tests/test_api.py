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
