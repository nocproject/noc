# ----------------------------------------------------------------------
# /api/login/login handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

# NOC modules
from noc.aaa.models.user import User
from noc.config import config
from ..models.login import LoginRequest
from ..models.status import StatusResponse
from ..auth import authenticate, set_jwt_cookie

router = APIRouter()

# Minimum time left to expire password
EXPIRATION_GUARD_TIME = 3_600


@router.post("/api/login/login", response_model=StatusResponse, tags=["login", "ext-ui"])
async def login(request: Request, creds: LoginRequest):
    auth_req = {"user": creds.user, "password": creds.password, "ip": request.client.host}
    user_name = authenticate(auth_req)
    if not user_name:
        # Failed
        return StatusResponse(status=False, message="Authentication failed")
    # Get user. Cannot use cached version
    user = User.objects.filter(username=user_name).first()
    if not user:
        return StatusResponse(status=False, message="Authentication failed")
    if not user.is_active:
        return StatusResponse(status=False, message="Authentication failed. User is not active")
    # Check password expiration
    if user.change_at:
        now = datetime.datetime.now()
        ttl = int((user.change_at - now).total_seconds())
        if ttl < EXPIRATION_GUARD_TIME:
            return ORJSONResponse({"status": True, "must_change": True})
    else:
        ttl = config.login.session_ttl
    # Generate JWT cookie
    response = ORJSONResponse({"status": True, "must_change": False})
    set_jwt_cookie(response, user_name, expire=ttl)
    return response
