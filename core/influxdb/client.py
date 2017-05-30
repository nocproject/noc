# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# InfluxDB client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import urllib
import cStringIO
# Third-party modules
import ujson
import pycurl
import six
# NOC modules
from noc.config import config


class InfluxDBClient(object):
    def __init__(self):
        pass

    def query(self, query):
        """
        Perform queries and return result
        :param query: String or list of queries
        """
        buff = cStringIO.StringIO()
        if not isinstance(query, six.string_types):
            query = ";".join(query)
        if isinstance(query, unicode):
            query = query.encode("utf-8")
        url = "http://%s/query?db=%s&q=%s" % (
            str(config.influxdb.addresses[0]),
            config.influxdb.db,
            urllib.quote(query)
        )
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buff)
        c.setopt(c.NOPROXY, "*")
        c.setopt(c.TIMEOUT, 30)
        c.setopt(c.CONNECTTIMEOUT, 3)
        try:
            c.perform()
        except pycurl.error as e:
            raise ValueError("Request error: %s" % e)
        finally:
            c.close()
        try:
            data = ujson.loads(buff.getvalue())
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
