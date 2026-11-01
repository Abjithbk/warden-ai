"""Domain exceptions. Services raise these; one handler maps them to HTTP."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class WardenError(Exception):
    status_code = 500

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class NotFoundError(WardenError):
    status_code = 404


class ConflictError(WardenError):
    status_code = 409


class PolicyDeniedError(ConflictError):
    pass


class ServiceUnavailableError(WardenError):
    status_code = 503


class UpstreamError(WardenError):
    status_code = 502


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(WardenError)
    async def _handle(_: Request, exc: WardenError) -> JSONResponse:
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)