# ----------------------------------------------------------------------
# /api/login/is_first_login/ path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

# NOC modules
from noc.aaa.models.user import User
from ..utils import is_hardened, DEFAULT_USER, DEFAULT_PASSWORD
from ..models.setadmin import SetAdminRequest
from ..models.status import StatusResponse

router = APIRouter()


@router.put("/api/login/set_admin/", tags=["login"])
async def set_admin(req: SetAdminRequest):
    """
    Set admin user and password on unhardened system.
    """
    if is_hardened():
        return StatusResponse(status=False, message="System is already hardened")
    if req.user == DEFAULT_USER:
        return StatusResponse(status=False, message=f"User may not be `{DEFAULT_USER}`")
    if req.password == DEFAULT_PASSWORD:
        return StatusResponse(status=False, message=f"Password may not be `{DEFAULT_PASSWORD}`")
    # Get user
    user = User.objects.get(username=DEFAULT_USER)
    user.username = req.user
    user.set_password(req.password)
    user.save()
    return StatusResponse(status=True, message="Credentials are changed")
