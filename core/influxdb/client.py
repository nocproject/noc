# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## InfluxDB client
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Import modules
import json
import urllib
## Third-party modules
import tornado.httpclient


class InfluxDBClient(object):
    def __init__(self):
        pass

    def query(self, query):
        """
        Perform queries and return result
        :param query: String or list of queries
        """
        if not isinstance(query, basestring):
            query = ";".join(query)
        url = "http://127.0.0.1:8086/query?db=noc&q=%s" % urllib.quote(query)
        client = tornado.httpclient.HTTPClient()
        response = client.fetch(url)
        data = json.loads(response.body)
        for qr in data["results"]:
            if not qr:
                continue
            for sv in qr["series"]:
                for v in sv["values"]:
                    values = sv.get("tags", {}).copy()
                    values.update(dict(zip(sv["columns"], v)))
                    values["_name"] = sv["name"]
                    yield values
