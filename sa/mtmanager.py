# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MapTask Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import itertools
import json
## Third-party modules
import tornado.httpclient
## NOC modules
from noc.core.service.catalog import ServiceCatalog

logger = logging.getLogger(__name__)


class MTManagerImplementation(object):
    def __init__(self, limit=0):
        self.limit = limit
        self.catalog = ServiceCatalog()
        self.tid = itertools.count(1)

    def run(self, object, script, params=None, timeout=None):
        """
        Run SA script and wait for result
        """
        client = tornado.httpclient.HTTPClient()
        tid = self.tid.next()
        if "." in script:
            # Leave only script name
            script = script.split(".")[-1]
        req = {
            "id": tid,
            "method": "script",
            "params": [object.id, script, params]
        }
        client = tornado.httpclient.HTTPClient()
        response = None
        for l in self.catalog.get_service("sae").listen:
            try:
                response = client.fetch(
                    "http://%s/api/sae/" % l,
                    method="POST",
                    body=json.dumps(req),
                    headers={
                        "X-NOC-Calling-Service": "MTManager"
                    }
                )
            except tornado.httpclient.HTTPError, why:
                if why.code in (404, 500):
                    raise Exception("Failed to call")
                continue
            except Exception, why:
                continue
        if not response:
            raise Exception("No SAE service found")
        data = json.loads(response.body)
        return data["result"]


# Run single instance
MTManager = MTManagerImplementation()
