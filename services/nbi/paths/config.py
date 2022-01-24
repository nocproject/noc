# ----------------------------------------------------------------------
# config API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Callable

# Third-party modules
from fastapi import APIRouter, Path, Header, HTTPException
from fastapi.responses import PlainTextResponse

# NOC modules
from noc.sa.models.managedobject import ManagedObject
from ..base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE

router = APIRouter()


class ConfigAPI(NBIAPI):
    api_name = "config"
    openapi_tags = ["config API"]

    def get_routes(self):
        route_config = {
            "path": "/api/nbi/config/{object_id}",
            "method": "GET",
            "endpoint": self.get_config_handler(),
            "response_class": PlainTextResponse,
            "response_model": None,
            "name": "config",
            "description": "Get last configuration for Managed Object with id `object_id`",
        }
        route_config_revision = {
            "path": "/api/nbi/config/{object_id}/{revision}",
            "method": "GET",
            "endpoint": self.get_config_revision_handler(),
            "response_class": PlainTextResponse,
            "response_model": None,
            "name": "config_revision",
            "description": "Get configuration revision `revision_id` for Managed Object with id `object_id`",
        }
        return [route_config, route_config_revision]

    def _handler(self, access_header, object_id, revision=None):
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        mo = ManagedObject.get_by_id(object_id)
        if not mo:
            raise HTTPException(404, "Not Found")
        if revision:
            if not mo.config.has_revision(revision):
                raise HTTPException(404, "Revision not found")
            config = mo.config.get_revision(revision)
        else:
            config = mo.config.read()
        if config is None:
            raise HTTPException(204, "")
        return config

    def get_config_handler(self) -> Callable:
        async def handler(
            object_id: int, access_header: str = Header(..., alias=API_ACCESS_HEADER)
        ):
            result = self._handler(access_header, object_id)
            return result

        return handler

    def get_config_revision_handler(self) -> Callable:
        async def handler(
            object_id: int,
            revision: str = Path(..., regex="^[0-9a-f]{24}$"),
            access_header: str = Header(..., alias=API_ACCESS_HEADER),
        ):
            result = self._handler(access_header, object_id, revision)
            return result

        return handler


# Install router
ConfigAPI(router)
