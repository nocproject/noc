# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## InfluxDB client
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import urllib
import cStringIO
## Third-party modules
import ujson
import pycurl
## NOC modules
from noc.core.config.base import config


class InfluxDBClient(object):
    def __init__(self):
        pass

    def query(self, query):
        """
        Perform queries and return result
        :param query: String or list of queries
        """
        buff = cStringIO.StringIO()
        if not isinstance(query, basestring):
            query = ";".join(query)
        svc = config.get_service("influxdb", limit=1)
        if not svc:
            raise ValueError("No service configured")
        url = "http://%s/query?db=%s&q=%s" % (
            svc[0],
            config.influx_db,
            urllib.quote(query)
        )
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buff)
        c.setopt(c.NOPROXY, "*")
        c.setopt(c.TIMEOUT, 60)
        c.setopt(c.CONNECTTIMEOUT, 3)
        try:
            c.perform()
        except pycurl.error as e:
            raise ValueError("Request error: %s" % e)
        finally:
            c.close()
        try:
            data = ujson.loads(buff.getvalue())
        except ValueError, why:
            raise ValueError("Failed to decode JSON: %s" % why)
        for qr in data["results"]:
            if not qr:
                continue
            for sv in qr["series"]:
                for v in sv["values"]:
                    values = sv.get("tags", {}).copy()
                    values.update(dict(zip(sv["columns"], v)))
                    values["_name"] = sv["name"]
                    yield values
