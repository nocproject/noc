## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## IP Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import MODiscoveryJob
from noc.inv.discovery.reports.macreport import MACReport
from noc.vc.models.vcdomain import VCDomain
from noc.settings import config
from noc.inv.models.subinterface import SubInterface


class MACDiscoveryJob(MODiscoveryJob):
    name = "mac_discovery"
    map_task = "get_mac_address_table"

    ignored = not config.getboolean("mac_discovery", "enabled")
    initial_submit_interval = config.getint("mac_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("mac_discovery",
        "initial_submit_concurrency")
    to_save = config.getboolean("mac_discovery", "save")

    def handler(self, object, result):
        """
        :param object:
        :param result:
        :return:
        """
        seen = {}  # MAC -> vlan
        dups = set()
        # Detect SVI addresses seen in multiple vlans
        for v in result:
            if v["type"] == "D":
                mac = v["mac"]
                vlan = v["vlan_id"]
                if mac in seen and seen[mac] != vlan:
                    # Duplicated
                    dups.add(mac)
                else:
                    seen[mac] = vlan
        # Fill report
        self.report = MACReport(self, to_save=self.to_save)
        vc_domain = VCDomain.get_for_object(self.object)
        for v in result:
            if (v["type"] == "D" and v["interfaces"] and
                v["mac"] not in dups):
                self.report.submit(
                    mac=v["mac"],
                    vc_domain=vc_domain,
                    vlan=v["vlan_id"],
                    managed_object=object,
                    if_name=v["interfaces"][0]
                )
        self.report.send()
        return True

    @classmethod
    def initial_submit_queryset(cls):
        return {"object_profile__enable_mac_discovery": True}

    @classmethod
    def can_submit(cls, object):
        """
        Check object has bridge interfaces
        :param cls:
        :param object:
        :return:
        """
        return object.is_managed and bool(
            SubInterface.objects.filter(managed_object=object.id,
                enabled_afi="BRIDGE").first())

    def can_run(self):
        if not super(MACDiscoveryJob, self).can_run():
            return False
        if not self.object.object_profile.enable_mac_discovery:
            return False
        # Check object has bridge interfaces
        # with enabled MAC discovery
        for si in SubInterface.objects.filter(
            managed_object=self.object.id,
            enabled_afi="BRIDGE"):
            try:
                iface = si.interface
            except Exception:
                continue  # Dereference failed
            if iface.profile.mac_discovery:
                return True
        # No suitable interfaces
        return False

    @classmethod
    def get_submit_interval(cls, object):
        return object.object_profile.mac_discovery_max_interval

    def get_failed_interval(self):
        return self.object.object_profile.mac_discovery_min_interval
