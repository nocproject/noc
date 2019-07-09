# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# telemetry API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
from collections import defaultdict

# Third-party modules
import tornado.gen
import ujson
import six

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
    @tornado.gen.coroutine
    def post(self):
        code, result = yield self.executor.submit(self.handler)
        self.set_status(code)
        if isinstance(result, six.string_types):
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
        chains = defaultdict(list)
        for (scope, path, ts), values in six.iteritems(data):
            # @todo: Proper key fields
            record_fields = ["%s.date.ts.managed_object" % scope]
            if path:
                record_fields += ["path"]
            fields = sorted(values)
            record_fields += fields
            rf = ".".join(record_fields)
            if isinstance(rf, unicode):
                rf = rf.encode("utf-8")
            # Convert timestamp to CH format
            ts = ts.replace("T", " ")
            date = ts.split()[0]
            # Build record
            record = [date, ts, bi_id]
            if path:
                record += [self.quote_path(path)]
            record += [str(values[f]) for f in fields]
            r = "\t".join(record)
            if isinstance(r, unicode):
                r = r.encode("utf-8")
            chains[rf] += [r]
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
