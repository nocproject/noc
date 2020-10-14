# ----------------------------------------------------------------------
# /api/login/login handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

# NOC modules
from ..models.login import LoginRequest
from ..models.status import StatusResponse
from ..auth import authenticate, set_jwt_cookie

router = APIRouter()


@router.post("/api/login/login", response_model=StatusResponse, tags=["login", "ext-ui"])
async def login(request: Request, creds: LoginRequest):
    auth_req = {"user": creds.user, "password": creds.password, "ip": request.client.host}
    user = authenticate(auth_req)
    if user:
        response = ORJSONResponse({"status": True})
        set_jwt_cookie(response, user)
        return response
    return StatusResponse(status=False, message="Authentication failed")
