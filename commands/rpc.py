# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RPC cli
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import json
import argparse
## Third-party modules
import tornado.httpclient
## NOC modules
from noc.core.management.base import BaseCommand
from noc.core.service.catalog import ServiceCatalog


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--config",
            action="store",
            dest="config",
            default=os.environ.get("NOC_CONFIG", "etc/noc.yml"),
            help="Configuration path"
        )
        parser.add_argument(
            "rpc",
            nargs=1,
            help="RPC name in form <api>[-<pool>].<method>"
        )
        parser.add_argument(
            "arguments",
            nargs=argparse.REMAINDER,
            help="Arguments passed to RPC calls"
        )

    def handle(self, config, rpc, arguments, *args, **options):
        catalog = ServiceCatalog(config)
        service, method = rpc[0].split(".", 1)
        api = service.split("-")[0]
        tid = 1
        req = {"id": tid, "method": method, "params": arguments}
        client = tornado.httpclient.HTTPClient()
        for l in catalog.get_service(service).listen:
            try:
                response = client.fetch(
                    "http://%s/api/%s/" % (l, api),
                    method="POST",
                    body=json.dumps(req)
                )
            except tornado.httpclient.HTTPError, why:
                if why.code in (404, 500):
                    self.die("Failed to call: %s" % why)
                continue
            except Exception, why:
                continue
            data = json.loads(response.body)
            if data.get("error"):
                self.die("Error: %s" % data.get("error"))
            else:
                self.stdout.write(str(data["result"]) + "\n")
                return
        self.die("No active services")

if __name__ == "__main__":
    Command().run()
