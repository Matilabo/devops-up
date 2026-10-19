# syntax=docker/dockerfile:1

# Imagen base fija (nunca "latest"): Python 3.12 slim sobre Debian trixie.
ARG PYTHON_IMAGE=python:3.12.15-slim-trixie

# ---- Etapa 1: dependencias ----
# Se instalan en un virtualenv que después se copia entero a la imagen final.
FROM ${PYTHON_IMAGE} AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Primero solo requirements.txt: si cambia el código pero no las dependencias,
# esta capa sale del caché y no se vuelve a descargar nada.
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---- Etapa 2: ejecución ----
FROM ${PYTHON_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Usuario sin privilegios con UID fijo. El código queda como propiedad de root,
# así que el proceso puede leerlo pero no modificarlo.
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY app ./app

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-m", "app.healthcheck"]

CMD ["python", "-m", "app"]
