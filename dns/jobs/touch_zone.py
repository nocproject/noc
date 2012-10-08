# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Update zone, change serial and send notifications
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.scheduler import Job
from noc.dns.models.dnszone import DNSZone
from noc.lib.scheduler.utils import sync_request


class TouchZoneJob(Job):
    name = "dns.touch_zone"
    ignored = False
    model = DNSZone

    def handler(self, *args, **kwargs):
        if not self.object.is_auto_generated:
            return True
        self.object.set_next_serial()
        self.object.update_repo()
        if self.data.get("new"):
            sync_request(self.object.channels, "list")
        else:
            sync_request(self.object.channels,
                "verify", self.object.name)
        return True
