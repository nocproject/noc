# ----------------------------------------------------------------------
# configrevisions API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
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

# TimestampType = constr(regex="^[a-z]$")


class Revision(BaseModel):
    # timestamp: TimestampType
    timestamp: str
    revision: str

    # @validator("timestamp")
    # def check_timestamp(cls, v):  # pylint: disable=no-self-argument
    #    print("v", v, type(v))
    #    return v


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
            revs = [
                {"revision": str(r.id), "timestamp": r.ts.isoformat()}
                for r in mo.config.get_revisions()
            ]
            return revs

        return handler


# Install router
ConfigRevisionsAPI(router)
