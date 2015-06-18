## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Prefix report
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python
import datetime
## NOC modules
from base import Report
from noc.main.models import PyRule
from noc.ip.models.prefix import Prefix
from noc.lib.ip import IP
from noc.inv.models.newprefixdiscoverylog import NewPrefixDiscoveryLog
from noc.settings import config


class PrefixReport(Report):
    system_notification = "inv.prefix_discovery"

    def __init__(self, job, enabled=True, to_save=False):
        super(PrefixReport, self).__init__(
            job, enabled=enabled, to_save=to_save)
        self.prefix_state_map = self.get_state_map(
            config.get("prefix_discovery", "change_state"))
        self.new_prefixes = []

    @classmethod
    def initialize(cls, scheduler):
        super(PrefixReport, cls).initialize(scheduler)
        cls.p_custom_pyrule = None
        if cls.save_prefix:
            p = config.get("prefix_discovery", "custom_pyrule")
            r = list(PyRule.objects.filter(name=p,
                    interface="IGetDiscoveryCustom"))
            if r:
                scheduler.info("Enabling prefix discovery custom pyRule '%s'" % p)
                cls.p_custom_pyrule = r[0]
            else:
                scheduler.error("Prefix discovery custom pyRule '%s' is not found. Ignoring." % p)

    def is_ignored_prefix(self, afi, prefix):
        return ((afi == "4" and (
                prefix.startswith("127.") or
                prefix.endswith("/32"))
            ) or
            (afi == "6" and (
                prefix.startswith("fe80:") or
                prefix.endswith("/128"))
            ))

    def submit(self, vrf, prefix, interface=None, description=None):
        if not self.enabled:
            return
        # Normalize prefix
        p = IP.prefix(prefix)
        prefix = str(p.normalized)
        # Ignore local prefixes
        if self.is_ignored_prefix(p.afi, prefix):
            return
        # Check prefix in IPAM
        afi = "6" if ":" in prefix else "4"
        r = Prefix.objects.filter(vrf=vrf, afi=afi, prefix=prefix)
        if r:
            self.change_prefix(r[0])  # Change existing address
        else:
            self.new_prefix(vrf, afi, prefix, interface, description)

    def new_prefix(self, vrf, afi, prefix,
                   interface=None, description=None):
        # Enable IPv4 AFI on VRF, if not set
        if afi == "4" and not vrf.afi_ipv4:
            self.info("Enabling IPv4 AFI on VRF %s (%s)" % (
                vrf.name, vrf.rd))
            if self.to_save:
                vrf.afi_ipv4 = True
                vrf.save()
        # Enable IPv6 AFI on VRF, if not set
        if afi == "6" and not vrf.afi_ipv6:
            self.info("Enabling IPv6 AFI on VRF %s (%s)" % (
                vrf.name, vrf.rd))
            if self.to_save:
                vrf.afi_ipv6 = True
                vrf.save()
        # Save prefix
        self.info("IPv%s prefix found: %s:%s" % (afi, vrf, prefix))
        self.new_prefixes += [{
            "vrf": vrf,
            "prefix": prefix,
            "object": self.object,
            "interface": interface,
            "description": description
        }]
        if self.to_save:
            Prefix(vrf=vrf, afi=afi,
                prefix=prefix, description=description).save()

    def change_prefix(self, prefix):
        if prefix.state.id in self.prefix_state_map:
            # Change address state
            fs = prefix.state
            ts = self.prefix_state_map[fs.id]
            self.info(
                "Changing prefix %s:%s state from %s to %s" % (
                    prefix.vrf.name, prefix.prefix,
                    fs.name, ts.name))
            if self.to_save:
                prefix.state = ts
                prefix.save()

    def submit_dual_stack(self, vrf, ipv4, ipv6):
        if not self.enabled:
            return
        try:
            p4 = Prefix.objects.get(vrf=vrf, afi="4",
                            prefix=str(IP.prefix(ipv4).normalized))
            p6 = Prefix.objects.get(vrf=vrf, afi="6",
                            prefix=str(IP.prefix(ipv6).normalized))
        except Prefix.DoesNotExist:
            return
        if not p4.has_transition and not p6.has_transition:
            self.info("Dual-stacking prefixes %s and %s" % (
                p4, p6))
            if self.to_save:
                p4.ipv6_transition = p6
                p4.save()

    def send(self):
        ts = datetime.datetime.now()
        log = [NewPrefixDiscoveryLog(
            timestamp=ts,
            vrf=p["vrf"].name,
            prefix=p["prefix"],
            description=p["description"],
            managed_object=p["object"].name,
            interface=p["interface"]) for p in self.new_prefixes]
        if log:
            NewPrefixDiscoveryLog.objects.insert(log, load_bulk=True)
            ctx = {
                "count": len(self.new_prefixes),
                "prefixes": [
                    {
                        "vrf": p["vrf"],
                        "prefix": p["prefix"],
                        "description": p["description"],
                        "object": p["object"],
                        "interface": p["interface"]
                    } for p in self.new_prefixes
                ]
            }
            self.notify("inv.discovery.new_prefixes_report", ctx)
