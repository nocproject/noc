# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# InfluxDB client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import urllib
# Third-party modules
import ujson
import six
# NOC modules
from noc.config import config
from noc.core.http.client import fetch_sync
from noc.config import config


class InfluxDBClient(object):
    REQUEST_TIMEOUT = config.influxdb.request_timeout
    CONNECT_TIMEOUT = config.influxdb.connect_timeout

    def __init__(self):
        pass

    def query(self, query):
        """
        Perform queries and return result
        :param query: String or list of queries
        """
        if not isinstance(query, six.string_types):
            query = ";".join(query)
        if isinstance(query, unicode):
            query = query.encode("utf-8")
        svc = config.get_service("influxdb", limit=1)
        if not svc:
            raise ValueError("No service configured")
        url = "http://%s/query?db=%s&q=%s" % (
            svc[0],
            config.influx_db,
            urllib.quote(query)
        )
        code, headers, body = fetch_sync(
            url,
            connect_timeout=self.CONNECT_TIMEOUT,
            request_timeout=self.REQUEST_TIMEOUT
        )
        if code != 200:
            raise ValueError("%s: %s" % (code, body))
        try:
            data = ujson.loads(body)
        except ValueError as e:
            raise ValueError("Failed to decode JSON: %s" % e)
        if type(data) == dict and "error" in data:
            raise ValueError(data["error"])
        for qr in data["results"]:
            if not qr:
                continue
            if "error" in qr:
                raise ValueError(qr["error"])
            if "series" not in qr:
                continue
            for sv in qr["series"]:
                for v in sv["values"]:
                    values = sv.get("tags", {}).copy()
                    values.update(dict(zip(sv["columns"], v)))
                    values["_name"] = sv["name"]
                    yield values
