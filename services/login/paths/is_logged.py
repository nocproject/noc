# ----------------------------------------------------------------------
# /api/login/is_logged/ path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from fastapi import APIRouter, Cookie
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
import orjson

# NOC modules
from noc.config import config
from noc.core.comp import smart_text

router = APIRouter()


@router.get("/api/login/is_logged/", tags=["login", "ext-ui"])
async def is_logged(jwt_cookie: Optional[str] = Cookie(None, alias=config.login.jwt_cookie_name)):
    """
    Check if user is logged
    """
    result = False
    if jwt_cookie:
        try:
            token = jwt.decode(
                jwt_cookie,
                smart_text(orjson.dumps(config.secret_key)),
                algorithms=[config.login.jwt_algorithm],
            )
            result = isinstance(token, dict) and "sub" in token
        except JWTError:
            pass
    return JSONResponse(result, status_code=200)
