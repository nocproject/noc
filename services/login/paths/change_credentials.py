# ----------------------------------------------------------------------
# /api/login/change_credentials handler
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse


# NOC modules
from noc.config import config
from ..auth import change_credentials as _change_credentials, ChangeCredentialsError, set_jwt_cookie
from ..models.changecredentials import ChangeCredentialsRequest
from ..models.status import StatusResponse

router = APIRouter()


@router.put(
    "/api/login/change_credentials", response_model=StatusResponse, tags=["login", "ext-ui"]
)
async def change_credentials(req: ChangeCredentialsRequest) -> StatusResponse:
    creds = {
        "user": req.user,
        "old_password": req.old_password,
        "new_password": req.new_password,
    }
    try:
        _change_credentials(creds)
    except ChangeCredentialsError as e:
        return StatusResponse(status=False, message=str(e))
    # Update login cookie
    response = ORJSONResponse({"status": True})
    set_jwt_cookie(response, req.user, expire=config.login.session_ttl)
    return response
