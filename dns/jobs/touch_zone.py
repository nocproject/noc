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

    def get_display_key(self):
        if self.object:
            return self.object.name
        else:
            return self.key

    def handler(self, *args, **kwargs):
        if not self.object.is_auto_generated:
            return True  # Not generated
        if not self.object.refresh_zone():
            return True  # Not changed
        # Send notifications
        if self.data.get("new"):
            sync_request(self.object.channels, "list")
        else:
            sync_request(self.object.channels,
                "verify", self.object.name)
        return True
