# ----------------------------------------------------------------------
# servicestatus API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import List, Union, Optional, Dict

# Third-party modules
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

# NOC modules
from noc.sa.models.service import Service
from noc.main.models.remotesystem import RemoteSystem
from ..base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE

router = APIRouter()


class ServiceStatus(BaseModel):
    id: int
    name: str


class ServiceId(BaseModel):
    id: str


class RemoteId(BaseModel):
    remote_system: str
    remote_id: str


class ServiceStatusRequest(BaseModel):
    services: List[Union[ServiceId, RemoteId]]
    changed_at: Optional[datetime.datetime] = None
    suppress_not_found: bool = False


class Status(BaseModel):
    id: str
    status: ServiceStatus
    change: datetime.datetime
    in_maintenance: bool = False
    parent: Optional[str] = None
    remote_mappings: Optional[Dict[str, str]] = None


class ServiceStatusResponse(BaseModel):
    statuses: List[Status]
    not_found_queries: Optional[List[Union[ServiceId, RemoteId]]] = None


class ServiceStatusAPI(NBIAPI):
    api_name = "servicestatus"
    openapi_tags = ["servicestatus API"]

    def get_routes(self):
        route = {
            "path": "/api/nbi/servicestatus",
            "method": "POST",
            "endpoint": self.handler,
            "response_model": ServiceStatusResponse,
            "name": "servicestatus",
            "description": "Get current statuses for one or more Services",
        }
        return [route]

    async def handler(
        self, req: ServiceStatusRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)
    ):
        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        # Validate
        ids = set()
        try:
            for o in req.services:
                if hasattr(o, "id"):
                    ids.add(o.id)
                    continue
                rs = RemoteSystem.get_by_name(o.remote_system)
                svc = Service.get_by_mapping(rs, o.remote_id)
                if svc:
                    ids.add(svc.id)
        except ValueError as e:
            raise HTTPException(400, "Bad request: %s" % e)
        if not ids:
            raise HTTPException(400, "Not requested service")
        statuses = []
        for svc_id, parent, status, change, mapps in Service.objects.filter(
            id__in=list(ids)
        ).scalar("id", "parent", "oper_status", "oper_status_change", "mappings"):
            r = {
                "id": str(svc_id),
                "status": {"id": status.value, "name": status.name},
                "in_maintenance": False,
                "change": change,
            }
            if parent:
                r["parent"] = parent
            if mapps:
                r["mappings"] = {m.remote_system.name: m.remote_id for m in mapps}
            statuses.append(r)
        return {"statuses": statuses}


# Install router
ServiceStatusAPI(router)
