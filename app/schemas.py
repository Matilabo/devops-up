"""Modelos de respuesta que documentan la API en Swagger."""

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str = Field(examples=["ok"])
    version: str = Field(examples=["1.0.0"])
    backend_available: bool = Field(description="Si el demonio de Docker responde")


class ContainerSummary(BaseModel):
    id: str = Field(examples=["3f4e8a1b2c9d"])
    name: str = Field(examples=["devops-up-demo-1"])
    image: str = Field(examples=["nginx:1.30.6-alpine"])
    status: str = Field(examples=["running"])


class ErrorResponse(BaseModel):
    detail: str = Field(examples=["No existe el contenedor 'abc123'"])
