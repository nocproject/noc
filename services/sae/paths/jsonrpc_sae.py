# ----------------------------------------------------------------------
# SAE JSON-RPC API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

# NOC modules
from noc.core.debug import error_report
from noc.core.error import NOCError
from noc.core.service.api import Redirect
from noc.core.service.loader import get_service
from noc.core.service.models.jsonrpc import JSONRemoteProcedureCall
from noc.services.sae.api.sae import SAEAPI

router = APIRouter()


@router.post("/api/sae/")
@router.post("/api/sae")
async def api_mib(req: JSONRemoteProcedureCall):
    if req.method not in SAEAPI.get_methods():
        return {"error": f"Invalid method: '{req.method}'", "id": req.id}
    service = get_service()
    api = SAEAPI(service, None, None)
    api_method = getattr(api, req.method)
    result = None
    error = None
    try:
        result = await api_method(*req.params)
    except NOCError as e:
        error = f"Failed: {e}"
    except Exception as e:
        error_report()
        error = f"Failed: {e}"
    if isinstance(result, Redirect):
        location = result.location
        result_redir = {"method": result.method, "params": result.params}
        return RedirectResponse(url=location) # content=result_redir
    return {"result": result, "error": error, "id": req.id}
