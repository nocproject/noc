## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MAC Discovery Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import Report
from noc.inv.models.interface import Interface
from noc.inv.models.macdb import MACDB


class MACReport(Report):
    system_notification = "inv.prefix_discovery"

    def __init__(self, job, enabled=True, to_save=False):
        super(MACReport, self).__init__(
            job, enabled=enabled, to_save=to_save)
        self.changed = []
        self.if_cache = {}

    def submit(self, mac, vc_domain, vlan, managed_object, if_name):
        if not self.enabled:
            return
        iface = self.get_interface(managed_object, if_name)
        if not iface:
            return  # Not found
        if not iface.profile.mac_discovery:
            return  # Disabled discovery
        if MACDB.submit(mac, vc_domain, vlan, iface):
            self.info("MAC %s. VC Domain: %s, VLAN %d at %s" % (
                mac,
                vc_domain.name if vc_domain else None,
                vlan, if_name))
            self.changed += [(mac, vlan, iface)]

    def get_interface(self, managed_object, if_name):
        if if_name in self.if_cache:
            return self.if_cache[if_name]
        si = Interface.objects.filter(
            managed_object=managed_object.id, name=if_name).first()
        self.if_cache[if_name] = si
        return si

    def send(self):
        if not self.changed:
            return
        # ctx = {}
        # self.notify("....", ctx)
