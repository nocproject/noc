# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Respond to STOMP requests
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.main.scheduler.jobs.sync import SyncJob
from noc.dns.models.dnszone import DNSZone
from noc.dns.models.dnsserver import DNSServer


class SyncDNSZoneCmdJob(SyncJob):
    name = "dns.sync_dns_zone_cmd"
    destination = "/queue/sync/dns/zone/"
    ignored = False

    def on_list(self, channel, object=None):
        """
        list command handler
        :param channel:
        :param object:
        :return:
        """
        # Get all related profiles
        profiles = set()
        for ns in DNSServer.objects.filter(sync_channel=channel):
            profiles |= set(ns.masters.all())
            profiles |= set(ns.slaves.all())
        # Get zone list
        zones = dict((z.name, z.serial)
            for z in DNSZone.objects.filter(
                is_auto_generated=True, profile__in=profiles))
        # Send LIST message
        self.send({
            "cmd": "list",
            "items": zones
        }, destination="/queue/sync/dns/zone/%s/" % channel)
        return True

    def on_verify(self, channel, object):
        try:
            z = DNSZone.objects.get(name=object)
            msg = {
                "cmd": "verify",
                "object": z.name,
                "data": {
                    "serial": z.serial,
                    "records": z.get_records()
                }
            }
        except DNSZone.DoesNotExist:
            # Force LIST request
            msg = {
                "cmd": "request",
                "request": "list"
            }
        self.send(msg, destination="/queue/sync/dns/zone/%s/" % channel)
        return True
