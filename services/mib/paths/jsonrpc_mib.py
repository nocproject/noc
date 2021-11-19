# ----------------------------------------------------------------------
# mib JSON-RPC API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter
from pydantic import BaseModel

# NOC modules
from noc.core.service.loader import get_service
from noc.services.mib.api.mib import MIBAPI

router = APIRouter()


class JSONRemoteProcedureCall(BaseModel):
    method: str
    params: list
    id: int


@router.post("/api/mib/")
@router.post("/api/mib")
def api_mib(incoming_call: JSONRemoteProcedureCall):
    for method in MIBAPI.get_methods():
        if incoming_call.method == method:
            service = get_service()
            api = MIBAPI(service, None, None)
            api_method = getattr(api, method)
            try:
                result = api_method(*incoming_call.params)
                error = None
            except Exception as e:
                result = None
                error = 'Failed: {}'.format(e)
            return {
                "result": result,
                "error": error,
                'id': incoming_call.id
            }
    return {
        "error": "Invalid method: '{}'".format(incoming_call.method),
        'id': incoming_call.id
    }
