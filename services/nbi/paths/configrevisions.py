# ----------------------------------------------------------------------
# configrevisions API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Callable

# Third-party modules
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel  # constr, validator

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from ..base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE

router = APIRouter()


class Revision(BaseModel):
    timestamp: str
    revision: str


class ConfigRevisionsAPI(NBIAPI):
    api_name = "configrevisions"
    openapi_tags = ["configrevisions API"]

    def get_routes(self):
        route = {
            "path": "/api/nbi/configrevisions/{object_id}",
            "method": "GET",
            "endpoint": self.get_configrevisions_handler(),
            "response_model": List[Revision],
            "name": "configrevisions",
            "description": "Get all config revisions for Managed Object with id `object_id`",
        }
        return [route]

    def get_configrevisions_handler(self) -> Callable:
        async def handler(
            object_id: int, access_header: str = Header(..., alias=API_ACCESS_HEADER)
        ):
            if not self.access_granted(access_header):
                raise HTTPException(403, FORBIDDEN_MESSAGE)
            mo = ManagedObject.get_by_id(object_id)
            if not mo:
                raise HTTPException(404, "Not Found")
            return [
                {"revision": str(r.id), "timestamp": r.ts.isoformat()}
                for r in mo.config.get_revisions()
            ]

        return handler


# Install router
ConfigRevisionsAPI(router)
