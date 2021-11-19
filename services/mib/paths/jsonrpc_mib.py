# ----------------------------------------------------------------------
# mib JSON-RPC API endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from fastapi import APIRouter

# NOC modules
from noc.core.service.loader import get_service
from noc.core.service.models.jsonrpc import JSONRemoteProcedureCall
from noc.services.mib.api.mib import MIBAPI

router = APIRouter()


@router.post("/api/mib/")
@router.post("/api/mib")
def api_mib(incoming_call: JSONRemoteProcedureCall):
    if incoming_call.method in MIBAPI.get_methods():
        service = get_service()
        api = MIBAPI(service, None, None)
        api_method = getattr(api, incoming_call.method)
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
    else:
        return {
            "error": "Invalid method: '{}'".format(incoming_call.method),
            'id': incoming_call.id
        }
