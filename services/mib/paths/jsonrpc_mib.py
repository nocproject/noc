# ----------------------------------------------------------------------
# mib JSON-RPC API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter

# NOC modules
from noc.core.debug import error_report
from noc.core.error import NOCError
from noc.core.service.loader import get_service
from noc.core.service.models.jsonrpc import JSONRemoteProcedureCall
from noc.services.mib.api.mib import MIBAPI

router = APIRouter()


@router.post("/api/mib/")
@router.post("/api/mib")
def api_mib(req: JSONRemoteProcedureCall):
    if req.method not in MIBAPI.get_methods():
        return {
            "error": f"Invalid method: '{req.method}'",
            "id": req.id
        }
    service = get_service()
    api = MIBAPI(service, None, None)
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
    return {
        "result": result,
        "error": error,
        "id": req.id
    }
