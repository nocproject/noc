# ----------------------------------------------------------------------
# getmappings API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import operator
from typing import Optional, List, Union

# Third-party modules
from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel

# NOC modules
from noc.models import get_model
from noc.main.models.remotesystem import RemoteSystem
from ..base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE

router = APIRouter()


class GetMappingsRequest(BaseModel):
    scope: Optional[str] = None
    id: Optional[Union[str, List[str]]] = None
    remote_system: Optional[str] = None
    remote_id: Optional[Union[str, List[str]]] = None


class Mapping(BaseModel):
    remote_system: str
    remote_id: str


class GetMappingsResponseItem(BaseModel):
    scope: str
    id: str
    mappings: List[Mapping]


class GetMappingsAPI(NBIAPI):
    api_name = "getmappings"
    openapi_tags = ["getmappings API"]
    SCOPES = {"managedobject": "sa.ManagedObject"}

    @staticmethod
    def cleaned_request(scope=None, id=None, remote_system=None, remote_id=None):
        def to_list(s):
            if s is None:
                return None
            if isinstance(s, list):
                return [str(x) for x in s]
            return [str(s)]

        if not scope:
            raise ValueError("scope must be set")
        if scope not in GetMappingsAPI.SCOPES:
            raise ValueError(f"Invalid scope: {scope}")
        if remote_id and not remote_system:
            raise ValueError("remote_system must be set")
        if not id and not remote_id:
            raise ValueError("At least one id or remote_id must be set")
        return {
            "scope": scope,
            "local_ids": to_list(id),
            "remote_system": remote_system if remote_id else None,
            "remote_ids": to_list(remote_id),
        }

    def get_routes(self):
        route_get = {
            "path": "/api/nbi/getmappings",
            "method": "GET",
            "endpoint": self.handler_get,
            "response_model": List[GetMappingsResponseItem],
            "name": "getmappings",
            "description": "Allows remote system to query mappings between NOC's local identifiers (ID) and the remote system's one.",
        }
        route_post = {
            "path": "/api/nbi/getmappings",
            "method": "POST",
            "endpoint": self.handler_post,
            "response_model": List[GetMappingsResponseItem],
            "name": "getmappings",
            "description": "Allows remote system to query mappings between NOC's local identifiers (ID) and the remote system's one.",
        }
        return [route_get, route_post]

    async def handler_get(
        self,
        scope: Optional[str] = None,
        id: Optional[List[str]] = Query(None),
        remote_system: Optional[str] = None,
        remote_id: Optional[List[str]] = Query(None),
        access_header: str = Header(..., alias=API_ACCESS_HEADER),
    ):
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        try:
            req = self.cleaned_request(
                scope=scope,
                id=id,
                remote_system=remote_system,
                remote_id=remote_id,
            )
        except ValueError as e:
            raise HTTPException(400, f"Bad request: {e}")
        return self.do_mapping(**req)

    async def handler_post(
        self, request: GetMappingsRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)
    ):
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        try:
            req = self.cleaned_request(
                scope=request.scope,
                id=request.id,
                remote_system=request.remote_system,
                remote_id=request.remote_id,
            )
        except ValueError as e:
            raise HTTPException(400, self.error_msg(f"Bad request: {e}"))
        return self.do_mapping(**req)

    @staticmethod
    def error_msg(msg):
        return {"status": False, "error": msg}

    def do_mapping(self, scope, local_ids=None, remote_system=None, remote_ids=None):
        """
        Perform mapping
        :param scope: scope name
        :param local_ids: List of Local id
        :param remote_system: Remote system id
        :param remote_ids: List of Id from remote system
        :return:
        """

        def format_obj(o):
            r = {"scope": scope, "id": str(o.id), "mappings": []}
            if o.remote_system:
                r["mappings"] += [
                    {"remote_system": str(o.remote_system.id), "remote_id": str(o.remote_id)}
                ]
            return r

        # Get model to query
        model = get_model(self.SCOPES[scope])
        if not model:
            raise HTTPException(400, self.error_msg("Invalid scope"))
        # Query remote objects
        result = []
        if remote_system and remote_ids:
            rs = RemoteSystem.get_by_id(remote_system)
            if not rs:
                raise HTTPException(404, self.error_msg("Remote system not found"))
            if len(remote_ids) == 1:
                qs = model.objects.filter(remote_system=rs.id, remote_id=remote_ids[0])
            else:
                qs = model.objects.filter(remote_system=rs.id, remote_id__in=remote_ids)
            result += [format_obj(o) for o in qs]
        # Query local objects
        seen = {o["id"] for o in result}
        # Skip already collected objects
        local_ids = local_ids or []
        local_ids = [o for o in local_ids if o not in seen]
        if local_ids:
            if len(local_ids) == 1:
                qs = model.objects.filter(id=local_ids[0])
            else:
                qs = model.objects.filter(id__in=local_ids)
            result += [format_obj(o) for o in qs]
        # 404 if no objects found
        if not result:
            raise HTTPException(404, self.error_msg("Not found"))
        return sorted(result, key=operator.itemgetter("id"))


# Install router
GetMappingsAPI(router)
