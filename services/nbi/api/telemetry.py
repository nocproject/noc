# ----------------------------------------------------------------------
# telemetry API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from collections import defaultdict

# Third-party modules
import ujson

# NOC modules
from noc.core.service.apiaccess import authenticated
from noc.sa.interfaces.base import (
    DictParameter,
    DictListParameter,
    StringParameter,
    StringListParameter,
    IntParameter,
    ListOfParameter,
    ListParameter,
)
from noc.pm.models.metrictype import MetricType
from ..base import NBIAPI


Request = DictParameter(
    attrs={
        "bi_id": IntParameter(required=True),
        "metrics": DictListParameter(
            attrs={
                "metric_type": StringParameter(required=True),
                "path": StringListParameter(required=True),
                "values": ListOfParameter(ListParameter(), required=True),
            },
            required=True,
        ),
    }
)


class TelemetryAPI(NBIAPI):
    name = "telemetry"

    @authenticated
    async def post(self):
        code, result = await self.executor.submit(self.handler)
        self.set_status(code)
        if isinstance(result, str):
            self.write(result)
        else:
            self.write(ujson.dumps(result))

    def handler(self):
        # Decode request
        try:
            req = ujson.loads(self.request.body)
        except ValueError:
            return 400, "Cannot decode JSON"
        # Validate
        try:
            req = Request.clean(req)
        except ValueError as e:
            return 400, "Bad request: %s" % e
        # Group metrics
        data = defaultdict(dict)  # (scope, path, ts) -> field -> value
        bi_id = str(req["bi_id"])
        for metric in req["metrics"]:
            mt = MetricType.get_by_name(metric["metric_type"])
            if not mt:
                self.logger.error("Unknown metric type '%s'. Skipping", metric["metric_type"])
                continue
            table = mt.scope.table_name
            field = mt.field_name
            path = tuple(metric["path"])
            for ts, value in metric["values"]:
                # @todo: Check timestamp
                # @todo: Check value type
                data[table, path, ts][field] = value
        # Prepare to send
        chains = defaultdict(list)  # table -> metrics
        for (scope, path, ts), values in data.items():
            # Convert timestamp to CH format
            ts = ts.replace("T", " ")
            date = ts.split()[0]
            # Metric record
            data = values  # Values first to protect critical fields
            data.update({"date": date, "ts": ts, "managed_object": bi_id})
            if path:
                data["path"] = [str(x) for x in path]
            chains[scope] += [data]
        # Spool metrics
        for f in chains:
            self.service.register_metrics(f, chains[f])
        return 200, "OK"

    @staticmethod
    def quote_path(path):
        """
        Convert path list to ClickHouse format
        :param path:
        :return:
        """
        return "[%s]" % ",".join("'%s'" % p for p in path)
