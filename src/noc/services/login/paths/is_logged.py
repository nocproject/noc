# ----------------------------------------------------------------------
# /api/login/is_logged/ path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from fastapi import APIRouter, Cookie
from fastapi.responses import JSONResponse
import jwt
from jwt import InvalidTokenError

# NOC modules
from noc.config import config

router = APIRouter()


@router.get("/api/login/is_logged/", tags=["login", "ext-ui"])
async def is_logged(jwt_cookie: str | None = Cookie(None, alias=config.login.jwt_cookie_name)):
    """
    Check if user is logged
    """
    result = False
    if jwt_cookie:
        try:
            token = jwt.decode(
                jwt_cookie,
                config.secret_key,
                algorithms=[config.login.jwt_algorithm],
                audience="auth",
            )
            result = isinstance(token, dict) and "sub" in token
        except InvalidTokenError:
            pass
    return JSONResponse(result, status_code=200)
