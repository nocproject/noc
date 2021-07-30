# ----------------------------------------------------------------------
# send endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional
from http import HTTPStatus

# Third-party modules
from fastapi import APIRouter, Header, HTTPException

# NOC modules
from noc.core.service.loader import get_service
from noc.pm.models.agent import Agent
from ..models.send import SendRequest

router = APIRouter()


@router.post("/api/metricscollector/send")
async def send(req: SendRequest, x_noc_agent_key: Optional[str] = Header(None)) -> None:
    if not x_noc_agent_key:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
    agent = Agent.objects.filter(key=x_noc_agent_key).first()
    if not agent:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
    # Spool data
    svc = get_service()
    svc.send_data(req.__root__)
