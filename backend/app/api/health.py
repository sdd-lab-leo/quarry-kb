"""Infrastructure health probes (SEC-01 exception; Compose/network boundary only)."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response

from app.core.envelope import error_envelope, success_envelope
from app.services.health_service import HealthService

router = APIRouter(prefix="/health", tags=["health"])


def _health_service(request: Request) -> HealthService:
    return request.app.state.health_service


@router.get("/live")
def live(request: Request) -> dict:
    service = _health_service(request)
    return success_envelope(service.liveness())


@router.get("/ready")
def ready(request: Request, response: Response) -> dict:
    service = _health_service(request)
    result = service.readiness()
    payload = {
        "status": result.status,
        "components": result.components,
    }
    if result.ready:
        response.status_code = 200
        return success_envelope(payload)
    response.status_code = 503
    return error_envelope(
        data=payload,
        code=result.error_code or "CONFIGURATION_INVALID",
        message=result.error_message or "Foundation is not ready.",
    )
