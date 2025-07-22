# ----------------------------------------------------------------------
# /api/login/login handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging

# Third-party modules
from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse

# NOC modules
from noc.aaa.models.user import User
from noc.config import config
from ..models.login import LoginRequest
from ..models.status import StatusResponse
from ..auth import authenticate, register_last_login, set_jwt_cookie

logger = logging.getLogger(__name__)
router = APIRouter()

# Minimum time left to expire password
EXPIRATION_GUARD_TIME = 3_600
BLOCK_ON_FAILED_LOGINS = config.login.max_failed_attempts > 0


@router.post("/api/login/login", response_model=StatusResponse, tags=["login", "ext-ui"])
async def login(request: Request, creds: LoginRequest):
    if BLOCK_ON_FAILED_LOGINS:
        # Check if account is blocked
        user = User.get_by_username_uncached(creds.user)
        if user:
            now = datetime.datetime.now()
            if user and user.blocked_till and user.blocked_till > now:
                delta = int((user.blocked_till - now).total_seconds())
                return StatusResponse(
                    status=False,
                    message=f"User is blocked for {delta}s",
                )
    auth_req = {"user": creds.user, "password": creds.password, "ip": request.client.host}
    user_name = authenticate(auth_req)
    if not user_name:
        # Failed
        if BLOCK_ON_FAILED_LOGINS:
            blocked_till = User.register_failed_login(creds.user)
            if blocked_till:
                delta = int((blocked_till - datetime.datetime.now()).total_seconds())
                logger.info("User %s is blocked for %ds", creds.user, delta)
                return StatusResponse(
                    status=False,
                    message=f"User is blocked for {delta}s",
                )
        return StatusResponse(status=False, message="Authentication failed")
    # Get user. Cannot use cached version
    user = User.get_by_username_uncached(user_name)
    if not user:
        return StatusResponse(status=False, message="Authentication failed")
    if not user.is_active:
        return StatusResponse(status=False, message="Authentication failed. User is not active")
    # Check inactivity of user
    if config.login.max_inactivity:
        last_login = user.last_login
        now = datetime.datetime.now()
        if last_login and int((now - last_login).total_seconds()) > config.login.max_inactivity:
            user.is_active, user.last_login = False, None
            user.save()
            logger.warning(
                "User '%s' was blocked for long inactivity time. Last login was: %s",
                user_name,
                last_login,
            )
            return StatusResponse(status=False, message="User is blocked for long inactivity time")
    register_last_login(user_name)
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
