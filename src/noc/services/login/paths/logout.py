# ----------------------------------------------------------------------
# /api/login/logout/ path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

# NOC modules
from noc.config import config

router = APIRouter()


@router.get("/api/login/logout/", tags=["login", "ext-ui"])
async def logout():
    """
    Logout and redirect to login screen
    """
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie(config.login.jwt_cookie_name)
    return response
