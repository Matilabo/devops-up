"""Backend simulado: contenedores en memoria para usar la API sin Docker (ej. en Render)."""

import hashlib
import random

from app.errors import ContainerNotFoundError, ContainerNotRunningError

# Nombre, imagen y memoria base en MiB de cada contenedor ficticio.
DEMO_CONTAINERS = (
    ("web", "nginx:1.30.6-alpine", 12.0),
    ("db", "postgres:17-alpine", 180.0),
    ("cache", "redis:8-alpine", 8.0),
)
MEMORY_LIMIT_MIB = 512.0


class SimulatorService:
    """Imita a DockerService con contenedores ficticios y métricas aleatorias."""

    def __init__(self, seed: int | None = None):
        self._random = random.Random(seed)
        self._containers = [
            {
                "id": hashlib.sha256(name.encode()).hexdigest()[:12],
                "name": name,
                "image": image,
                "status": "running",
                "base_memory_mib": memory,
            }
            for name, image, memory in DEMO_CONTAINERS
        ]

    def ping(self) -> bool:
        return True

    def list_containers(self) -> list[dict]:
        return [
            {key: container[key] for key in ("id", "name", "image", "status")}
            for container in self._containers
            if container["status"] == "running"
        ]

    def get_stats(self, ref: str) -> dict:
        container = self._find(ref)
        if container["status"] != "running":
            raise ContainerNotRunningError(ref)

        usage = round(container["base_memory_mib"] * self._random.uniform(0.9, 1.1), 2)
        return {
            "id": container["id"],
            "name": container["name"],
            "cpu_percent": round(self._random.uniform(0.1, 25.0), 2),
            "memory_usage_mib": usage,
            "memory_limit_mib": MEMORY_LIMIT_MIB,
            "memory_percent": round(usage / MEMORY_LIMIT_MIB * 100, 2),
        }

    def restart(self, ref: str, timeout: int = 10) -> dict:
        return self._set_status(ref, "restart", "running")

    def stop(self, ref: str, timeout: int = 10) -> dict:
        return self._set_status(ref, "stop", "exited")

    def _set_status(self, ref: str, action: str, status: str) -> dict:
        container = self._find(ref)
        container["status"] = status
        return {"id": container["id"], "name": container["name"], "action": action, "status": status}

    def _find(self, ref: str) -> dict:
        # Igual que Docker: acepta el nombre, el ID completo o un prefijo del ID.
        for container in self._containers:
            if ref == container["name"] or container["id"].startswith(ref):
                return container
        raise ContainerNotFoundError(ref)
