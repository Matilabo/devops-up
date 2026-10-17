# devops-up

API REST que se conecta al demonio de Docker local (SDK oficial) para listar contenedores, consultar su consumo de CPU y memoria, y reiniciarlos o detenerlos.

Trabajo práctico integrador de DevOps · Universidad de Palermo

## Integrantes
- Risek Abucharara
- Matias Laboratto

## Requisitos
- Docker Desktop o Docker Engine
- Python 3.12 (solo para desarrollo local)

## Cómo ejecutar
```bash
docker compose up --build
```
La documentación interactiva queda en http://localhost:8000/docs

## Endpoints
| Método | Ruta | Descripción |
|---|---|---|
| GET | /containers | Lista contenedores activos |
| GET | /containers/{id}/stats | CPU y memoria del contenedor |
| POST | /containers/{id}/restart | Reinicia el contenedor |
| POST | /containers/{id}/stop | Detiene el contenedor |

## Tests
```bash
pytest
```

## Flujo de trabajo
- `main` está protegida: todo cambio entra por Pull Request con al menos una revisión.
- Ramas: `feat/...`, `fix/...`, `ci/...`, `docs/...`.
- Commits según [Conventional Commits](CONTRIBUTING.md).
- Versionado según [SemVer](https://semver.org/lang/es/). Cada tag `vX.Y.Z` publica una imagen con ese tag en Docker Hub.

## Pipeline CI/CD
_Pendiente: diagrama y descripción de los workflows._

## Monitoreo
_Pendiente: dashboard de New Relic y señales doradas._

## Decisiones de diseño
_Pendiente: imagen base, multi-stage, usuario non-root, estrategia de branching._
