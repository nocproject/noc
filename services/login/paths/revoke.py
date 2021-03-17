# ----------------------------------------------------------------------
# Revoke tokens
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter, Depends

# NOC modules
from ..auth import get_user_from_jwt
from ..models.revoke import RevokeRequest
from ..models.status import StatusResponseError, StatusResponse
from noc.core.service.deps.service import get_service
from noc.services.login.service import LoginService


router = APIRouter()


@router.post("/api/login/revoke", tags=["login"])
async def revoke(req: RevokeRequest, svc: LoginService = Depends(get_service)):
    if req.access_token:
        try:
            get_user_from_jwt(req.access_token, audience="auth")
        except ValueError:
            return StatusResponseError(
                error="unauthorized_client", error_description="Invalid access token"
            )
        await svc.revoke_token(req.access_token)
    if req.refresh_token:
        try:
            get_user_from_jwt(req.refresh_token, audience="auth")
        except ValueError:
            return StatusResponseError(
                error="invalid_request", error_description="Invalid refresh token"
            )
        await svc.revoke_token(req.refresh_token)
    if not req.access_token and not req.refresh_token:
        return StatusResponseError(
            error="invalid_request", error_description="Invalid refresh token"
        )
    return StatusResponse(status=True, message="Ok")
