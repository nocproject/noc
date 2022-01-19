# ----------------------------------------------------------------------
# configrevisions API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
# from typing import Optional

# Third-party modules
from fastapi import APIRouter, Response, Header

# NOC modules
from noc.core.service.loader import get_service
from noc.sa.models.managedobject import ManagedObject

API_NAME = __name__.split(".")[-1]

API_ACCESS_HEADER = "X-NOC-API-Access"
ACCESS_TOKENS_SET = {"nbi:*", f"nbi:{API_NAME}"}

FORBIDDEN_MESSAGE = "<html><title>403: Forbidden</title><body>403: Forbidden</body></html>"

router = APIRouter()

service = get_service()
executor = service.get_executor("max")


def _access_granted(access_header):
    a_set = set(access_header.split(","))
    if ACCESS_TOKENS_SET & a_set:
        return True
    return False


def _handler(access_header, object_id):
    if not _access_granted(access_header):
        return 403, FORBIDDEN_MESSAGE
    mo = ManagedObject.get_by_id(int(object_id))
    if not mo:
        return 404, "Not Found"
    revs = [
        {"revision": str(r.id), "timestamp": r.ts.isoformat()} for r in mo.config.get_revisions()
    ]
    return 200, revs


@router.get("/api/nbi/configrevisions/{object_id}")
async def api_configrevisions(
    object_id: int, access_header: str = Header(..., alias=API_ACCESS_HEADER)
):
    code, result = await executor.submit(_handler, access_header, object_id)
    if isinstance(result, str):
        return Response(status_code=code, content=result, media_type="text/plain")
    else:
        return result
