import json
import logging
import sys
import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response

logger = logging.getLogger("taskflow")


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {"event": record.getMessage(), "level": record.levelname}
        if isinstance(record.args, dict):
            payload.update(record.args)
        return json.dumps(payload)


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False


def log_event(event: str, **fields: object) -> None:
    logger.info(event, fields)


def add_request_logging(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_requests(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = uuid4().hex
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # An unhandled exception is exactly the request most worth
            # tracing — log it before re-raising rather than letting it
            # skip this middleware's logging entirely.
            log_event(
                "request",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=500,
                latency_ms=round((time.perf_counter() - start) * 1000, 2),
            )
            raise
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        log_event(
            "request",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency_ms=latency_ms,
        )
        response.headers["X-Request-ID"] = request_id
        return response
