"""Public authentication and current-user routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import auth_service, require_active_user
from app.core.envelope import success_envelope
from app.services.auth_service import AuthenticatedUser, AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=1)
    password: str = Field(min_length=1)


@router.post("/login")
def login(body: LoginRequest, service: AuthService = Depends(auth_service)) -> dict:
    data = service.login(body.identifier, body.password)
    return success_envelope(data)


@router.get("/me")
def me(
    service: AuthService = Depends(auth_service),
    user: AuthenticatedUser = Depends(require_active_user),
) -> dict:
    return success_envelope(service.current_user_summary(user))
