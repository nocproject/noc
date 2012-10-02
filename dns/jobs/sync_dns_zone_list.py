# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Send VERIFY sync message
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import random
## NOC modules
from noc.lib.scheduler.intervaljob import IntervalJob
from noc.dns.models.dnsserver import DNSServer


class SyncDNSZoneVerify(IntervalJob):
    name = "dns.sync_dns_zone_list"
    threaded = True

    ignored = False
    initial_submit_interval = 300
    initial_submit_concurrency = 0
    success_retry = 24 * 3600
    failed_retry = 300

    @classmethod
    def initial_submit(cls, scheduler, keys):
        channels = set(c for c in
            DNSServer.objects.values_list("sync_channel", flat=True)
            if c and c not in keys
        )
        now = datetime.datetime.now()
        isc = cls.initial_submit_concurrency
        for c in channels:
            cls.submit(
                scheduler=scheduler,
                key=c,
                interval=cls.success_retry,
                failed_interval=cls.failed_retry,
                randomize=True,
                ts=now + datetime.timedelta(
                    seconds=random.random() * cls.initial_submit_interval))
            isc -= 1
            if not isc:
                break

    def handler(self, *args, **kwargs):
        dst = "/queue/sync/dns/zone/%s/" % self.key
        self.scheduler.daemon.stomp_client.send({
            "cmd": "request",
            "request": "list"
        }, dst)
        return True
