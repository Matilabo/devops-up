# Guía de contribución

## Ramas
`main` está protegida: nadie pushea directo. Cada cambio sale de `main` en una rama corta y vuelve por Pull Request.

| Prefijo | Para qué |
|---|---|
| `feat/...` | Funcionalidad nueva |
| `fix/...` | Corrección de un error |
| `ci/...` | Workflows de GitHub Actions |
| `docs/...` | Documentación |

## Commits: Conventional Commits
Formato: `tipo: descripción corta en minúscula`. Ejemplos de este repo:

```
feat: agregar endpoint para listar contenedores activos
fix: usar 127.0.0.1 por defecto en el script de tráfico
test: probar el backend simulador
ci: ejecutar lint y tests en cada pull request
```

| Tipo | Uso | Efecto en la versión |
|---|---|---|
| `feat` | Funcionalidad nueva | MINOR |
| `fix` | Corrección | PATCH |
| `docs`, `test`, `ci`, `build`, `style`, `refactor`, `chore` | Resto de cambios | Ninguno |
| `feat!` o pie `BREAKING CHANGE:` | Cambio incompatible | MAJOR |

## Pull Requests
1. Completar la plantilla: descripción, tipo de cambio, cómo se probó y evidencia.
2. El título del PR sigue Conventional Commits.
3. Esperar los checks del CI en verde (`lint`, `test` y `docker`).
4. Pedir la revisión del otro integrante.
5. Integrar con **Create a merge commit** para conservar el historial de commits.

## Antes de abrir el PR
```bash
pip install -r requirements-dev.txt
flake8
pytest
```

## Versionado (SemVer)
Para publicar una versión, crear el tag desde `main` actualizada:

```bash
git tag v1.0.0
git push origin v1.0.0
```

El workflow `Release` valida el tag, publica `usuario/devops-up:1.0.0` en Docker Hub, crea la release en GitHub y dispara el deploy en Render.
