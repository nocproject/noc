# ----------------------------------------------------------------------
# objectstatus API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List

# Third-party modules
from fastapi import APIRouter, Response, Header
from pydantic import BaseModel

# NOC modules
from noc.core.service.loader import get_service
from noc.sa.models.objectstatus import ObjectStatus

API_NAME = __name__.split(".")[-1]

API_ACCESS_HEADER = "X-NOC-API-Access"
ACCESS_TOKENS_SET = {"nbi:*", f"nbi:{API_NAME}"}

FORBIDDEN_MESSAGE = "<html><title>403: Forbidden</title><body>403: Forbidden</body></html>"

router = APIRouter()

service = get_service()
executor = service.get_executor("max")


class RequestModel(BaseModel):
    objects: List[str]


def _access_granted(access_header):
    a_set = set(access_header.split(","))
    if ACCESS_TOKENS_SET & a_set:
        return True
    return False


def _handler(access_header, objects_):
    if not _access_granted(access_header):
        return 403, FORBIDDEN_MESSAGE
    # Validate
    try:
        objects = [int(o) for o in objects_]
    except ValueError as e:
        return 400, "Bad request: %s" % e
    statuses = ObjectStatus.get_statuses(objects)
    r = {"statuses": [{"id": str(o), "status": statuses.get(o, False)} for o in objects]}
    return 200, r


@router.post("/api/nbi/objectstatus")
async def api_objectstatus(
    req: RequestModel, access_header: str = Header(..., alias=API_ACCESS_HEADER)
):
    code, result = await executor.submit(_handler, access_header, req.objects)
    if isinstance(result, str):
        return Response(status_code=code, content=result, media_type="text/plain")
    else:
        return result
