# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Service command
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
import consul
## NOC modules
from noc.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.out("Creating Consul Client", 1)
        c = consul.Consul()
        self.out("Requesting services", 1)
        s_mask = "%-20s %-10s %-30s %s"
        print s_mask % ("Service", "Node", "URL", "Tags")
        index, service = c.catalog.services()
        for sn in service:
            index, instances = c.catalog.service(sn)
            for si in instances:
                print s_mask % (
                    si["ServiceName"],
                    si["Node"],
                    "http://%s:%s/api/%s/" % (
                        si["Address"], si["ServicePort"],
                        si["ServiceName"]
                    ),
                    ""
                )

if __name__ == "__main__":
    Command().run()
