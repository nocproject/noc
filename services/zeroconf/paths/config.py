# ----------------------------------------------------------------------
# config endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List
from http import HTTPStatus

# Third-party modules
from fastapi import APIRouter, Query, Header, HTTPException

# NOC modules
from ..models.zk import ZkConfig
from ..util import find_agent, get_config

router = APIRouter()


@router.get("/api/zeroconf/config", response_model=ZkConfig)
def config(
    agent_id: Optional[str] = None,
    serial: Optional[str] = None,
    mac: Optional[List[str]] = Query(None),
    ip: Optional[List[str]] = Query(None),
    x_noc_agent_key: Optional[str] = Header(None),
    host: Optional[str] = Header(None),
    x_forwarded_proto: Optional[str] = Header(None),
):
    if agent_id and not x_noc_agent_key:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
    agent = find_agent(agent_id=agent_id, serial=serial, mac=mac, ip=ip)
    if not agent:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    if agent_id and agent.key != x_noc_agent_key:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
    if agent.profile.update_addresses:
        agent.update_addresses(serial=serial, mac=mac, ip=ip)
    # Get request auth level
    if agent_id and x_noc_agent_key:
        req_level = 2
    else:
        req_level = 1
    # Compare with expected level
    exp_level = agent.auth_level
    if req_level < exp_level:
        agent.fire_event("fail")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
    auth_level = min(req_level, agent.auth_level)
    # Base url
    scheme = x_forwarded_proto if x_forwarded_proto else "http"
    host = host or "localhost"
    base = f"{scheme}://{host}"
    cfg = get_config(agent, level=auth_level, base=base)
    agent.fire_event("seen")
    return cfg
