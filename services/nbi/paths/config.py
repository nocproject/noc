# ----------------------------------------------------------------------
# config API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
# from typing import Optional

# Third-party modules
from fastapi import APIRouter, Response, Path, Header

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


def _handler(access_header, object_id, revision=None):
    if not _access_granted(access_header):
        return 403, FORBIDDEN_MESSAGE
    mo = ManagedObject.get_by_id(object_id)
    if not mo:
        return 404, "Not Found"
    if revision:
        if not mo.config.has_revision(revision):
            return 404, "Revision not found"
        config = mo.config.get_revision(revision)
    else:
        config = mo.config.read()
    if config is None:
        return 204, ""
    return 200, config


@router.get("/api/nbi/config/{object_id}")
async def api_config(object_id: int, access_header: str = Header(..., alias=API_ACCESS_HEADER)):
    code, result = await executor.submit(_handler, access_header, object_id)
    return Response(status_code=code, content=result, media_type="text/plain")


@router.get("/api/nbi/config/{object_id}/{revision}")
async def api_config_revision(
    object_id: int,
    revision: str = Path(..., regex="^[0-9a-f]{24}$"),
    access_header: str = Header(..., alias=API_ACCESS_HEADER),
):
    code, result = await executor.submit(_handler, access_header, object_id, revision)
    return Response(status_code=code, content=result, media_type="text/plain")
