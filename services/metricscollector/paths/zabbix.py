# ----------------------------------------------------------------------
# Zabbix endpoints
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
import logging
import asyncio
import enum
from collections import defaultdict
from typing import Optional
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
ZABBIX_COLLECTOR = "zabbix"


class ValueType(enum.Enum):
    FLOAT = 0
    CHAR = 1
    LOG = 2
    UNSIGNED = 3
    TEXT = 4
    BINARY = 5


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
        metrics["msg_in", ("collector", ZABBIX_COLLECTOR)] += 1
        rs_cfg = self.service.get_remote_system_by_code(remote_system_code)
        if not rs_cfg or rs_cfg.is_banned:
            # IP Address
            return ORJSONResponse(
                {
                    "error": f"Unknown Remote System {remote_system_code}",
                },
                status_code=HTTPStatus.NOT_FOUND,
            )
        if rs_cfg.api_key != key:
            return ORJSONResponse(
                {
                    "error": f"Remote System API Key not Authorization {remote_system_code}",
                },
                status_code=HTTPStatus.FORBIDDEN,
            )
        received = defaultdict(dict)
        sensors = []
        # Clock, Name
        # Log request
        received_count = 0
        for line in req.split(b"\n"):
            if not line:
                continue
            # Linux: CPU guest nice time', 'clock': 1758647522, 'ns': 830065411, 'value': 0, 'type': 0
            item = orjson.loads(line)
            received_count += 1
            # metrics["items_in", ("collector", "zabbix")] += 1
            if item["type"] == ValueType.FLOAT.value or item["type"] == ValueType.UNSIGNED.value:
                # Add serial_num tag, to metrics.../or dict managed_object
                # Try sensor
                sensor_cfg = self.service.lookup_remote_sensor(item["itemid"], rs_cfg.name)
                if sensor_cfg:
                    ts = datetime.datetime.fromtimestamp(item["clock"])
                    sensors.append(((sensor_cfg, rs_cfg.bi_id), (ts, item["value"])))
                    continue
                received[(item["clock"], item["host"]["name"])][item["name"]] = item["value"]
        logger.debug("Received lines: %s", received_count)
        if sensors:
            logger.info("Received sensors: %s", len(sensors))
            self.service.send_sensors(sensors)
        if not received:
            return ORJSONResponse({}, status_code=200)
        r = []
        for (clock, host_name), metric in received.items():
            cfg = self.service.lookup_source_by_name(
                host_name, collector=ZABBIX_COLLECTOR
            )  # receiver
            if not cfg:
                continue
            ts = datetime.datetime.fromtimestamp(clock)
            if cfg.no_data_check:
                self.service.no_data_checker.register_data(
                    str(cfg.bi_id),
                    ts,
                    collector="metricscollector",
                    remote_system=rs_cfg.name,
                )
            metric["_units"] = {}
            r.append(
                SendMetric(
                    ts=ts,
                    collector=ZABBIX_COLLECTOR,
                    managed_object=cfg.bi_id,
                    remote_system=rs_cfg.bi_id,
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
        metrics["msg_in", ("collector", ZABBIX_COLLECTOR)] += 1
        rs_cfg = self.service.get_remote_system_by_code(remote_system_code)
        if not rs_cfg or rs_cfg.is_banned:
            # IP Address
            return ORJSONResponse(
                {
                    "error": f"Unknown Remote System {remote_system_code}",
                },
                status_code=HTTPStatus.NOT_FOUND,
            )
        if rs_cfg.api_key != authorization:
            return ORJSONResponse(
                {
                    "error": f"Remote System API Key not Authorization {remote_system_code}",
                },
                status_code=HTTPStatus.FORBIDDEN,
            )
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
                remote_system=rs_cfg.name,
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
            description="Integration with Zabbix Items Connector",
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
            name=f"{self.api_name}_zabbix_events",
            description="Integration with Zabbix Events Connector",
        )
        # AgentV1
        # AgentV2


# Install endpoints
ZabbixAPI(router)
