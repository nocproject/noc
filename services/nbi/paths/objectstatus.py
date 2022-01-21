# ----------------------------------------------------------------------
# objectstatus API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Callable

# Third-party modules
from fastapi import APIRouter, Response, Header
from pydantic import BaseModel

# NOC modules
from noc.sa.models.objectstatus import ObjectStatus
from ..base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE

router = APIRouter()


class RequestModel(BaseModel):
    objects: List[str]


class Status(BaseModel):
    id: str
    status: bool


class ResponseModel(BaseModel):
    statuses: List[Status]


class _ObjectStatusAPI(NBIAPI):
    api_name = "objectstatus"
    openapi_tags = ["objectstatus API"]

    def get_routes(self):
        route = {
            "path": "/api/nbi/objectstatus",
            "method": "POST",
            "endpoint": self.get_objectstatus_handler(),
            "response_model": ResponseModel,
            "name": "objectstatus",
            "description": "Get current statuses for one or more Managed Objects.",
        }
        return [route]

    def get_objectstatus_handler(self) -> Callable:
        async def objectstatus_handler(
            req: RequestModel, access_header: str = Header(..., alias=API_ACCESS_HEADER)
        ):
            def _handler(objects_):
                if not self.access_granted(access_header):
                    return 403, FORBIDDEN_MESSAGE
                # Validate
                try:
                    objects = [int(o) for o in objects_]
                except ValueError as e:
                    return 400, "Bad request: %s" % e
                statuses = ObjectStatus.get_statuses(objects)
                r = {
                    "statuses": [{"id": str(o), "status": statuses.get(o, False)} for o in objects]
                }
                return 200, r

            code, result = _handler(req.objects)
            if isinstance(result, str):
                return Response(status_code=code, content=result, media_type="text/plain")
            else:
                return result

        return objectstatus_handler


# Install router
_ObjectStatusAPI(router)
