# ----------------------------------------------------------------------
# BH endpoints
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio

# Third-party modules
from fastapi import APIRouter
from gufo.ping import Ping
from gufo.traceroute import Traceroute

# NOC modules
from ..models.bulk_ping import PingRequest, PingResponse
from ..models.traceroute import TracerouteRequest, TracerouteResponse

BULK_PING_TIMEOUT = 5
BULK_PING_INTERVAL = 0.1
BULK_PING_MAX_JOBS = 6

router = APIRouter()


@router.post("/api/bh/bulk_ping/")
async def bulk_ping(req: PingRequest):
    async def ping_worker():
        nonlocal result
        while True:
            async with lock:
                if not req.addresses:
                    break  # Done
                address = req.addresses.pop(0)
            rtt_list = []
            async for rtt in ping.iter_rtt(address, interval=BULK_PING_INTERVAL, count=req.n):
                rtt_list += [rtt]
            result += [{"address": address, "rtt": rtt_list}]

    timeout = req.timeout or BULK_PING_TIMEOUT
    result = []
    ping = Ping(tos=req.tos, timeout=timeout)
    lock = asyncio.Lock()
    tasks = [
        asyncio.create_task(ping_worker(), name=f"ping-{i}")
        for i in range(min(BULK_PING_MAX_JOBS, len(req.addresses)))
    ]
    await asyncio.gather(*tasks)
    return PingResponse(items=result)


@router.post("/api/bh/traceroute/")
async def traceroute(req: TracerouteRequest):
    items = []
    async with Traceroute(timeout=req.timeout, tos=req.tos) as tr:
        async for hop_info in tr.traceroute(req.address, tries=3):
            items += [hop_info]
    address = {h.addr for h in hop_info.hops if h is not None}
    if len(address) == 1:
        address = address.pop()  # single address
    elif len(address) == 0:
        address = ""  # empty address
    else:
        address = str(address)  # set of addresses
    return TracerouteResponse(status=address == req.address, end_address=address, items=items)
