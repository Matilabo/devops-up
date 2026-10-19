"""Logs estructurados en JSON: una línea por evento, lista para la plataforma de monitoreo."""

import json
import logging
from datetime import datetime, timezone

# Atributos que se pasan con `extra=` y se copian al JSON.
EXTRA_FIELDS = ("method", "path", "status_code", "duration_ms")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc)
        event = {
            "timestamp": timestamp.isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for field in EXTRA_FIELDS:
            if hasattr(record, field):
                event[field] = getattr(record, field)
        if record.exc_info:
            event["exception"] = self.formatException(record.exc_info)
        return json.dumps(event, ensure_ascii=False)


def build_log_config(level: str) -> dict:
    """Configuración para `logging.config.dictConfig`: la app y uvicorn loguean en JSON."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"json": {"()": JsonFormatter}},
        "handlers": {
            "stdout": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            }
        },
        # Los loggers de uvicorn no tienen handler propio: propagan al root.
        "loggers": {"uvicorn": {"handlers": [], "propagate": True}},
        "root": {"handlers": ["stdout"], "level": level},
    }
