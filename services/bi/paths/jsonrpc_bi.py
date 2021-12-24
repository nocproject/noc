# ----------------------------------------------------------------------
# BI JSON-RPC API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import namedtuple

# Third-party modules
from fastapi import APIRouter, Depends

# NOC modules
from noc.aaa.models.user import User
from noc.core.debug import error_report
from noc.core.error import NOCError
from noc.core.service.deps.user import get_current_user
from noc.core.service.loader import get_service
from noc.core.service.models.jsonrpc import JSONRemoteProcedureCall
from noc.services.bi.api.bi import BIAPI

RequestHandler = namedtuple("RequestHandler", ["current_user"])

router = APIRouter()


@router.post("/api/bi/")
@router.post("/api/bi")
def api_bi(req: JSONRemoteProcedureCall, current_user: User = Depends(get_current_user)):
    if req.method not in BIAPI.get_methods():
        return {"error": f"Invalid method: '{req.method}'", "id": req.id}
    service = get_service()
    request_handler = RequestHandler(current_user)
    api = BIAPI(service, None, request_handler)
    api_method = getattr(api, req.method)
    result = None
    error = None
    try:
        result = api_method(*req.params)
    except NOCError as e:
        error = f"Failed: {e}"
    except Exception as e:
        error_report()
        error = f"Failed: {e}"
    return {"result": result, "error": error, "id": req.id}
