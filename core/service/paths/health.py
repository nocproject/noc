# ----------------------------------------------------------------------
# /health path
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

# NOC modules
from noc.core.service.loader import get_service

router = APIRouter()


@router.get("/health", tags=["internal"])
@router.get("/health/", tags=["internal"])
async def health(service: Optional[str] = None):
    svc = get_service()
    if service and not svc.is_valid_health_check(service):
        return PlainTextResponse(content="Invalid service id", status_code=400)
    status, message = svc.get_health_status()
    # Watchdog
    if svc.watchdog_waiter and not svc.watchdog_waiter.is_set():
        svc.watchdog_waiter.set()
    return PlainTextResponse(content=message, status_code=status)
