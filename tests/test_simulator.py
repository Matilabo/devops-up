import pytest
from fastapi.testclient import TestClient

from app.errors import ContainerNotFoundError, ContainerNotRunningError
from app.main import app, get_service
from app.simulator import SimulatorService


@pytest.fixture
def simulator():
    return SimulatorService(seed=42)


def test_lista_los_contenedores_de_demo(simulator):
    names = [container["name"] for container in simulator.list_containers()]

    assert names == ["web", "db", "cache"]


def test_busca_por_nombre_o_prefijo_de_id(simulator):
    web = simulator.list_containers()[0]

    assert simulator.get_stats("web")["id"] == web["id"]
    assert simulator.get_stats(web["id"][:4])["name"] == "web"


def test_estadisticas_dentro_de_rangos(simulator):
    stats = simulator.get_stats("db")

    assert 0 < stats["cpu_percent"] <= 25
    assert 0 < stats["memory_percent"] < 100


def test_detener_saca_al_contenedor_de_la_lista(simulator):
    simulator.stop("cache")

    assert "cache" not in [c["name"] for c in simulator.list_containers()]
    with pytest.raises(ContainerNotRunningError):
        simulator.get_stats("cache")


def test_reiniciar_vuelve_a_ponerlo_en_ejecucion(simulator):
    simulator.stop("web")

    assert simulator.restart("web")["status"] == "running"


def test_contenedor_inexistente(simulator):
    with pytest.raises(ContainerNotFoundError):
        simulator.stop("no-existe")


@pytest.fixture
def simulator_client(simulator):
    app.dependency_overrides[get_service] = lambda: simulator
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_flujo_completo_por_http(simulator_client):
    assert simulator_client.post("/containers/web/stop").json()["status"] == "exited"
    assert simulator_client.get("/containers/web/stats").status_code == 409
    assert simulator_client.post("/containers/web/restart").json()["status"] == "running"
    assert simulator_client.get("/containers/web/stats").status_code == 200
