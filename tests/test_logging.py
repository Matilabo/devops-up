import json
import logging

from app.logging_config import JsonFormatter


def make_record(**extra):
    record = logging.LogRecord(
        name="app.requests",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="GET %s -> %s",
        args=("/containers", 200),
        exc_info=None,
    )
    record.__dict__.update(extra)
    return record


def test_formatea_el_evento_como_json():
    record = make_record(method="GET", path="/containers", status_code=200, duration_ms=3.2)

    event = json.loads(JsonFormatter().format(record))

    assert event["level"] == "INFO"
    assert event["message"] == "GET /containers -> 200"
    assert event["path"] == "/containers"
    assert event["status_code"] == 200
    assert event["duration_ms"] == 3.2
    assert event["timestamp"].endswith("+00:00")


def test_omite_campos_que_no_vienen_en_el_evento():
    event = json.loads(JsonFormatter().format(make_record()))

    assert "status_code" not in event
