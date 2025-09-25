# ----------------------------------------------------------------------
# telemetry API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict
from typing import Tuple, Optional, Set, List, Any

# Third-party modules
from fastapi import APIRouter, Header, HTTPException, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

# NOC modules
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType
from ..base import NBIAPI, API_ACCESS_HEADER, FORBIDDEN_MESSAGE

router = APIRouter()


class Metric(BaseModel):
    metric_type: str
    labels: List[str]
    values: List[List[Any]]


class TelemetryRequest(BaseModel):
    bi_id: int
    metrics: List[Metric]


class TelemetryAPI(NBIAPI):
    api_name = "telemetry"
    openapi_tags = ["telemetry API"]

    def get_routes(self):
        route = {
            "path": "/api/nbi/telemetry",
            "method": "POST",
            "endpoint": self.handler,
            "response_class": PlainTextResponse,
            "response_model": None,
            "name": "telemetry",
            "description": "Allows remote agents to push collected metrics to NOC",
        }
        return [route]

    async def handler(
        self, req: TelemetryRequest, access_header: str = Header(..., alias=API_ACCESS_HEADER)
    ):
        def get_scope(label: str) -> Tuple[Optional[str], str]:
            scope, *value = label.rsplit("::", 1)
            if not value:
                return None, scope
            return scope, value[0]

        def get_scope_key_label(scope: MetricScope) -> Set[str]:
            r = set()
            for ll in scope.labels:
                if ll.is_required or ll.is_primary_key:
                    r.add(ll.label[:-3])
            return r

        if not self.access_granted(access_header):
            raise HTTPException(403, FORBIDDEN_MESSAGE)
        # Group metrics
        data = defaultdict(dict)  # (scope, path, ts) -> field -> value
        bi_id = req.bi_id
        for metric in req.metrics:
            mt: MetricType = MetricType.get_by_name(metric.metric_type)
            if not mt:
                self.logger.error("Unknown metric type '%s'. Skipping", metric.metric_type)
                continue
            table = mt.scope.table_name
            field = mt.field_name
            labels = []
            label_scopes = set()
            for ll in metric.labels:
                scope, value = get_scope(ll)
                label_scopes.add(scope)
                labels.append(ll)
            kl = get_scope_key_label(mt.scope)
            if kl - label_scopes:
                HTTPException(400, f"Required Label for scope: {kl - label_scopes}")
            # Check Labels by Scope
            for ts, value in metric.values:
                # @todo: Check timestamp
                # @todo: Check value type
                data[table, tuple(labels), ts][field] = mt.clean_value(value)
        # Prepare to send
        chains = defaultdict(list)  # table -> metrics
        for (table, labels, ts), values in data.items():
            # Convert timestamp to CH format
            ts = ts.replace("T", " ")
            date = ts.split()[0]
            # Metric record
            data = values  # Values first to protect critical fields
            data.update({"date": date, "ts": ts, "managed_object": bi_id})
            if labels:
                data["labels"] = [str(x) for x in labels]
            chains[table] += [data]
        # Spool metrics
        for f in chains:
            self.service.register_metrics(f, chains[f])
        return Response(content="OK", media_type="text/html")


# Install router
TelemetryAPI(router)
