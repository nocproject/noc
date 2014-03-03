# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Send VERIFY sync message
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.main.scheduler.jobs.model import ModelJob
from noc.dns.models.dnszone import DNSZone


class SyncDNSZoneVerify(ModelJob):
    name = "dns.sync_dns_zone_verify"
    model = DNSZone
    # threaded = True

    ignored = False
    initial_submit_interval = 300
    initial_submit_concurrency = 0
    success_retry = 24 * 3600
    failed_retry = 300

    max_delay = 300
    delay_interval = 300

    def get_display_key(self):
        if self.object:
            return self.object.name
        else:
            return self.key

    @classmethod
    def can_submit(cls, object):
        return True  # @todo: Leave only provisioned zones

    def handler(self, *args, **kwargs):
        channels = self.object.channels
        if not channels:
            return True  # Not synchronized
        for c in channels:
            dst = "/queue/sync/%s/" % c
            self.send({
                "cmd": "request",
                "request": "verify",
                "object": self.object.name
            }, dst)
        return True
