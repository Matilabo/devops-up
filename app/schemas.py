"""Modelos de respuesta que documentan la API en Swagger."""

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str = Field(examples=["ok"])
    version: str = Field(examples=["1.0.0"])
    backend: str = Field(description="`docker` (SDK real) o `simulator`", examples=["docker"])
    backend_available: bool = Field(description="Si el backend responde")


class ContainerSummary(BaseModel):
    id: str = Field(examples=["3f4e8a1b2c9d"])
    name: str = Field(examples=["devops-up-demo-1"])
    image: str = Field(examples=["nginx:1.30.6-alpine"])
    status: str = Field(examples=["running"])


class ContainerStats(BaseModel):
    id: str = Field(examples=["3f4e8a1b2c9d"])
    name: str = Field(examples=["devops-up-demo-1"])
    cpu_percent: float = Field(description="Uso de CPU en %, como `docker stats`", examples=[1.25])
    memory_usage_mib: float = Field(description="Memoria usada sin caché, en MiB", examples=[12.4])
    memory_limit_mib: float = Field(description="Límite de memoria, en MiB", examples=[7837.5])
    memory_percent: float = Field(description="Memoria usada sobre el límite (%)", examples=[0.16])


class ActionResult(BaseModel):
    id: str = Field(examples=["3f4e8a1b2c9d"])
    name: str = Field(examples=["devops-up-demo-1"])
    action: str = Field(examples=["restart"])
    status: str = Field(description="Estado después de la acción", examples=["running"])


class ErrorResponse(BaseModel):
    detail: str = Field(examples=["No existe el contenedor 'abc123'"])
