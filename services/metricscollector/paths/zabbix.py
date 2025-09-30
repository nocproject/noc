# ----------------------------------------------------------------------
# Zabbix endpoints
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import cachetools
import logging
import asyncio
import enum
from collections import defaultdict
from typing import Optional, Set
from http import HTTPStatus

# Third-party modules
import orjson
from fastapi import APIRouter, Header, HTTPException, Body
from fastapi.responses import ORJSONResponse

# NOC modules
from noc.core.perf import metrics
from noc.core.service.loader import get_service
from noc.core.ioloop.util import setup_asyncio
from noc.core.fm.event import Event, Target, MessageType
from ..models.sendmetric import SendMetric


router = APIRouter()

logger = logging.getLogger(__name__)

API_ACCESS_HEADER = "X-NOC-API-Access"


class ValueType(enum.Enum):
    FLOAT = 0
    CHAR = 1
    LOG = 2
    UNSIGNED = 3
    TEXT = 4
    BINARY = 5


@cachetools.cached(cachetools.TTLCache(maxsize=50, ttl=60))
def get_format_role(ds, fmt):
    return ds.get_format_role(fmt)


def get_access_tokens_set(datastream, fmt: Optional[str] = None) -> Set[str]:
    tokens = {"datastream:*", f"datastream:{datastream.name}"}
    if fmt:
        role = get_format_role(datastream, fmt)
        if role:
            tokens.add(f"datastream:{role}")
    return tokens


class ZabbixAPI(object):
    def __init__(self, router: APIRouter):
        self.router = router
        self.openapi_tags = ["api", "metricscollector"]
        self.api_name = "metricscollector"
        self.ds_queue = {}
        setup_asyncio()
        self.loop = asyncio.get_event_loop()
        self.service = get_service()
        self.setup_endpoints()

    async def send(
        self,
        remote_system_code: str,
        req: bytes = Body(...),
        authorization: Optional[str] = Header(None, alias="Authorization"),
    ) -> ORJSONResponse:
        if not authorization:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
        _, key = authorization.split(" ")
        metrics["msg_in", ("collector", "zabbix")] += 1
        rs_name = self.service.get_remote_system_name(remote_system_code)
        if not rs_name:
            # raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
            return ORJSONResponse({}, status_code=200)
        received = defaultdict(dict)
        # Clock, Name
        # Log request
        for line in req.split(b"\n"):
            if not line:
                continue
            # Linux: CPU guest nice time', 'clock': 1758647522, 'ns': 830065411, 'value': 0, 'type': 0
            item = orjson.loads(line)
            # metrics["items_in", ("collector", "zabbix")] += 1
            if item["type"] == ValueType.FLOAT.value or item["type"] == ValueType.UNSIGNED.value:
                # Add serial_num tag, to metrics.../or dict managed_object
                received[(item["clock"], item["host"]["name"])][item["name"]] = item["value"]
        if not received:
            return ORJSONResponse({}, status_code=200)
        r = []
        for (clock, host_name), metric in received.items():
            cfg = self.service.lookup_source_by_name(host_name, collector="zabbix")  # receiver
            if not cfg:
                continue
            # if not cfg.has_remote_system(remote_system_code):
            # Optionally? Strict Mode, Pass Mode
            # print("Remote System not supported on item: ", cfg.name, cfg.remote_systems)
            #    continue
            metric["_units"] = {}
            r.append(
                SendMetric(
                    ts=datetime.datetime.fromtimestamp(clock),
                    collector="zabbix",
                    managed_object=cfg.bi_id,
                    # replace to code
                    # To labels ?
                    remote_system=rs_name,
                    metrics=metric,
                )
            )
        self.service.send_data(r)
        return ORJSONResponse({}, status_code=200)

    async def events(
        self,
        remote_system_code: str,
        req: bytes = Body(...),
        authorization: Optional[str] = Header(None, alias="Authorization"),
    ) -> ORJSONResponse:
        if not authorization:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
        logger.debug("REQUEST: %r", req)
        _, key = authorization.split(" ")
        metrics["msg_in", ("collector", "zabbix")] += 1
        rs_name = self.service.get_remote_system_name(remote_system_code)
        if not rs_name:
            # raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
            return ORJSONResponse({}, status_code=200)
        for line in req.split(b"\n"):
            if not line:
                continue
            item = orjson.loads(line)
            metrics["zabbix_events_in"] += 1
            if "p_eventid" in item:
                continue
            host_name = item["hosts"][0]["name"]
            cfg = self.service.lookup_source_by_name(host_name)
            if not cfg:
                continue
            event = Event(
                ts=item["clock"],
                target=Target(name=host_name, address=cfg.address),
                data=[],
                type=MessageType(),
                remote_id=str(item["eventid"]),
                remote_system=rs_name,
                message=item["name"],
                labels=[f"{t['tag']}::{t['value']}" for t in item["tags"]],
            )
            logger.info("Received %s event", event)
        # Spool data
        # Spool Format
        return ORJSONResponse({}, status_code=200)

    def setup_endpoints(self):
        # Items
        self.router.add_api_route(
            path=f"/api/{self.api_name}/zabbix/items/{{remote_system_code}}/send",
            endpoint=self.send,
            methods=["POST"],
            # dependencies=[Depends(self.get_verify_token_hander(ds))],
            # response_model=sig.return_annotation,
            # response_model=,
            tags=self.openapi_tags,
            name=f"{self.api_name}_zabbix_items",
            description=f"Integration with Zabbix Items Connector",
        )
        # Event
        self.router.add_api_route(
            path=f"/api/{self.api_name}/zabbix/events/{{remote_system_code}}/send",
            endpoint=self.events,
            methods=["POST"],
            # dependencies=[Depends(self.get_verify_token_hander(ds))],
            # response_model=sig.return_annotation,
            # response_model=,
            tags=self.openapi_tags,
            name=f"{self.api_name}_zabbix_items",
            description=f"Integration with Zabbix Events Connector",
        )
        # AgentV1
        # AgentV2


# Install endpoints
ZabbixAPI(router)
