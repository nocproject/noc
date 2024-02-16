# ----------------------------------------------------------------------
# /api/login/is_first_login/ path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

# NOC modules
from ..utils import is_hardened

router = APIRouter()


@router.get("/api/login/is_first_login/", tags=["login"])
async def is_first_login():
    """
    Check if it is first login into system and we need
    to change user name and password.
    """
    return ORJSONResponse({"status": not is_hardened()}, status_code=200)
