"""Admin user management routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, Field

from app.api.deps import account_service, require_admin
from app.core.envelope import success_envelope
from app.services.account_service import AccountService
from app.services.auth_service import AuthenticatedUser

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


class CreateUserRequest(BaseModel):
    identifier: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    password: str = Field(min_length=1)
    role: str = Field(min_length=1)


class UpdateUserRequest(BaseModel):
    display_name: str | None = None
    role: str | None = None
    status: str | None = None


@router.get("")
def list_users(
    _: AuthenticatedUser = Depends(require_admin),
    service: AccountService = Depends(account_service),
) -> dict:
    return success_envelope(service.list_users())


@router.post("")
def create_user(
    body: CreateUserRequest,
    response: Response,
    _: AuthenticatedUser = Depends(require_admin),
    service: AccountService = Depends(account_service),
) -> dict:
    data = service.create_user(
        identifier=body.identifier,
        display_name=body.display_name,
        password=body.password,
        role=body.role,
    )
    response.status_code = 201
    return success_envelope(data)


@router.patch("/{user_id}")
def update_user(
    user_id: UUID,
    body: UpdateUserRequest,
    _: AuthenticatedUser = Depends(require_admin),
    service: AccountService = Depends(account_service),
) -> dict:
    data = service.update_user(
        user_id,
        display_name=body.display_name,
        role=body.role,
        status=body.status,
    )
    return success_envelope(data)
