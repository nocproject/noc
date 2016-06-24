# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service command
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import argparse
## Third-party modules
## NOC modules
from noc.core.management.base import BaseCommand
from noc.core.service.catalog import ServiceCatalog
from noc.lib.text import format_table


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
            "services",
            nargs=argparse.REMAINDER,
            help="Service names"
        )

    def handle(self, config, services=None, *args, **options):
        catalog = ServiceCatalog(config)
        services = set(services or [])
        # Enumerate services
        out = [["S", "Service", "Node", "DC", "URL"]]
        for sn in catalog.iter_services():
            if services and sn not in services:
                continue
            sd = catalog.get_service(sn)
            for sn in sd.nodes:
                if sd.external:
                    url = sn.listen
                else:
                    nsn = sd.name.split("-")[0]
                    url = "http://%s/api/%s/" % (sn.listen, nsn)
                out += [[
                    " ",
                    sd.name,
                    sn.node,
                    sn.dc,
                    url
                ]]

        self.stdout.write(
            format_table(
                [0, 0, 0, 0, 0],
                out
            ) + "\n"
        )

if __name__ == "__main__":
    Command().run()
