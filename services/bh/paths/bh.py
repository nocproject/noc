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
from gufo.snmp import SnmpSession
from gufo.traceroute import Traceroute

# NOC modules
from noc.config import config
from ..models.bulk_ping import PingRequest, PingResponse
from ..models.bulk_snmp import SNMPRequest, SNMPResponse
from ..models.traceroute import TracerouteRequest, TracerouteResponse

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
            async for rtt in ping.iter_rtt(
                address, interval=config.bh.bulk_ping_interval, count=req.n
            ):
                rtt_list += [rtt]
            result += [{"address": address, "rtt": rtt_list}]

    timeout = req.timeout or config.bh.bulk_ping_timeout
    result = []
    ping = Ping(tos=req.tos, timeout=timeout)
    lock = asyncio.Lock()
    tasks = [
        asyncio.create_task(ping_worker(), name=f"ping-{i}")
        for i in range(min(config.bh.bulk_ping_max_jobs, len(req.addresses)))
    ]
    await asyncio.gather(*tasks)
    return PingResponse(items=result)


@router.post("/api/bh/bulk_snmp/")
async def bulk_snmp(req: SNMPRequest):
    async def snmp_worker():
        nonlocal result
        while True:
            async with lock:
                if not req.addresses:
                    break  # Done
                addr = req.addresses.pop(0)
            objects_list = []
            try:
                async with SnmpSession(
                    addr=addr.address, community=addr.community, timeout=timeout, tos=tos
                ) as session:
                    async for oid, value in session.getbulk(req.oid_filter):
                        objects_list += [(oid, value)]
                error_code = None
            except TimeoutError:
                error_code = "Timeout reached"
            result += [{"address": addr.address, "objects": objects_list, "error_code": error_code}]

    timeout = req.timeout or config.bh.bulk_snmp_timeout
    tos = req.tos or 0
    result = []
    lock = asyncio.Lock()
    tasks = [
        asyncio.create_task(snmp_worker(), name=f"snmp-{i}")
        for i in range(min(config.bh.bulk_snmp_max_jobs, len(req.addresses)))
    ]
    await asyncio.gather(*tasks)
    return SNMPResponse(items=result)


@router.post("/api/bh/traceroute/")
async def traceroute(req: TracerouteRequest):
    items = []
    async with Traceroute(timeout=req.timeout, tos=req.tos) as tr:
        async for hop_info in tr.traceroute(req.address, tries=config.bh.traceroute_tries):
            items += [hop_info]
    address = {h.addr for h in hop_info.hops if h is not None}
    if len(address) == 1:
        address = address.pop()  # single address
    elif len(address) == 0:
        address = ""  # empty address
    else:
        address = str(address)  # set of addresses
    return TracerouteResponse(status=address == req.address, end_address=address, items=items)
