# ----------------------------------------------------------------------
# send endpoint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
import logging
from typing import Optional, Any, List, Tuple
from http import HTTPStatus

# Third-party modules
import snappy
import zstd
from google.protobuf.message import DecodeError
from fastapi import APIRouter, Header, HTTPException, Body, Request
from fastapi.responses import ORJSONResponse

# NOC modules
from noc.core.service.loader import get_service
from noc.core.ioloop.util import setup_asyncio
from noc.core.perf import metrics
from ..models.vmagent import WriteRequest
from ..models.channel import RemoteSystemChannel

VMAGENT_COLLECTOR = "vmagent"
METRIC_LABEL_NAME = "__name__"
INSTANCE_LABEL_NAME = "instance"
JOB_LABEL_NAME = "job"
NODE_LABEL_NAMES = frozenset(["node", "host"])
MS = 1000

router = APIRouter()

logger = logging.getLogger(__name__)


class VMAgentAPI(object):
    """
    # https://github.com/prometheus/prometheus/blob/v2.24.0/prompb/remote.proto
    # https://prometheus.io/docs/specs/prw/remote_write_spec/
    # https://github.com/leegin/remote_pb2
    """

    def __init__(self, router: APIRouter):
        self.router = router
        self.openapi_tags = ["api", "metricscollector"]
        self.api_name = "metricscollector"
        self.ds_queue = {}
        setup_asyncio()
        self.loop = asyncio.get_event_loop()
        self.service = get_service()
        self.setup_endpoints()

    @staticmethod
    def parse_labels(
        labels: List[Any],
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Tuple[str, ...]]:
        """Parse input labels"""
        name, instance, host, r = None, None, None, []
        for ll in labels:
            if ll.name == JOB_LABEL_NAME:
                continue
            if ll.name == METRIC_LABEL_NAME:
                name = ll.value
            elif ll.name == INSTANCE_LABEL_NAME:
                instance = ll.value
            elif ll.name in NODE_LABEL_NAMES:
                host = ll.value
            elif ll.name == "cpu":
                r.append(f"noc::{ll.name}::{ll.value}")
            else:
                r.append(f"{ll.name}::{ll.value}")
        if not host and instance:
            host, *port = instance.split(":", 1)
        return name, instance, host, tuple(r)

    async def send(
        self,
        request: Request,
        req: bytes = Body(...),
        remote_system_code: Optional[str] = None,
        authorization: Optional[str] = Header(None, alias="Authorization"),
        content_encoding: Optional[str] = Header(None, alias="content-encoding"),
        remote_write_version: Optional[str] = Header(
            None, alias="x-victoriametrics-remote-write-version"
        ),
    ) -> ORJSONResponse:
        if not authorization:
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
        _, key = authorization.split(" ")
        metrics["msg_in", ("collector", VMAGENT_COLLECTOR)] += 1
        rs_cfg = self.service.get_remote_system_by_key(key.strip())
        if not rs_cfg or rs_cfg.is_banned:
            metrics[
                "error", ("type", "unknown_remote_system"), ("collector", VMAGENT_COLLECTOR)
            ] += 1
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
        metrics[
            "remote_msg_in", ("collector", VMAGENT_COLLECTOR), ("remote_system", rs_cfg.name)
        ] += 1
        # Lock ?
        channel: Optional[RemoteSystemChannel] = self.service.get_channel(
            rs_cfg,
            VMAGENT_COLLECTOR,
            batch_delay=30,
        )
        if not channel or channel.is_banned:
            # IP Address
            return ORJSONResponse(
                {
                    "error": f"Not Found Remote System by key {remote_system_code}",
                },
                status_code=HTTPStatus.NOT_FOUND,
            )
        received = 0
        if content_encoding == "zstd":
            req = zstd.decompress(req)
        else:
            req = snappy.uncompress(req)
        parser = WriteRequest()
        try:
            parser.ParseFromString(req)
        except DecodeError as e:
            logger.error("Error when parsed: %s", str(e))
            return ORJSONResponse({}, status_code=200)
        logger.debug("VMAgent, Parsed %s", parser)
        for ts in parser.timeseries:
            metric_name, instance, host, labels = self.parse_labels(ts.labels)
            if not metric_name:
                continue
            if not host:
                continue
            await channel.feed(
                host,
                metric_name,
                [(int(s.timestamp / MS), s.value) for s in ts.samples],
                labels=labels,
            )
            received += 1
        if received:
            logger.info(
                "[%s|%s] Received series: %s", self.api_name, channel.remote_system.name, received
            )
        return ORJSONResponse({}, status_code=200)

    def setup_endpoints(self):
        self.router.add_api_route(
            path=f"/api/{self.api_name}/vmagent/send",
            endpoint=self.send,
            methods=["POST"],
            # dependencies=[Depends(self.get_verify_token_hander(ds))],
            # response_model=sig.return_annotation,
            # response_model=,
            tags=self.openapi_tags,
            name=f"{self.api_name}_vmagen_metrics",
            description="Integration with VMAgent Prometheus-compatible metrics",
        )


# Install endpoints
VMAgentAPI(router)
