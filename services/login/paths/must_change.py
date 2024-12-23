# ----------------------------------------------------------------------
# /api/login/must_change/ path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from fastapi import APIRouter, Cookie
from fastapi.responses import ORJSONResponse

# NOC modules
from noc.config import config
from noc.aaa.models.user import User
from ..auth import get_user_from_jwt

router = APIRouter()


@router.get("/api/login/must_change/", tags=["login", "ext-ui"])
async def must_change(jwt_cookie: str | None = Cookie(None, alias=config.login.jwt_cookie_name)):
    """
    Check if user must change password
    """
    if jwt_cookie is None:
        return ORJSONResponse({"status": False}, status_code=401)
    try:
        user_name = get_user_from_jwt(jwt_cookie, audience="auth")
    except ValueError:
        return ORJSONResponse({"status": False}, status_code=401)
    user = User.get_by_username(user_name)
    if not user:
        return ORJSONResponse({"status": False}, status_code=401)
    if user.change_at and user.change_at < datetime.datetime.now():
        return ORJSONResponse({"status": True, "must_change": True})
    return ORJSONResponse({"status": True, "must_change": False})
