#!./bin/python
# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Periodic Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import MODiscoveryJob
from noc.fm.models.uptime import Uptime
from noc.inv.models.interface import Interface
from noc.vc.models.vcdomain import VCDomain
from noc.inv.models.macdb import MACDB


class PeriodicDiscoveryJob(MODiscoveryJob):
    name = "periodic"

    def handler(self, **kwargs):
        if self.object.object_profile.enable_periodic_discovery_uptime:
            self.logger.info("Checking uptime")
            self.check_uptime()
        if self.object.object_profile.enable_periodic_discovery_interface_status:
            has_interfaces = "DB | Interfaces" in self.object.get_caps()
            if has_interfaces:
                self.logger.info("Checking interface statuses")
                self.check_interface_status()
            else:
                self.logger.info("No interfaces discovered. "
                                 "Skipping interface status check")
        if self.object.object_profile.enable_periodic_discovery_mac:
            self.logger.info("Checking MAC addresses")
            self.check_mac()

    def can_run(self):
        return (
            self.object.is_managed and
            self.object.object_profile.enable_periodic_discovery and
            self.object.object_profile.periodic_discovery_interval
        )

    def get_interval(self):
        return self.object.object_profile.periodic_discovery_interval

    def get_failed_interval(self):
        return self.object.object_profile.periodic_discovery_interval

    def check_uptime(self):
        """
        Uptime discovery
        """
        uptime = self.object.scripts.get_uptime()
        self.logger.info("[uptime] Received uptime: %s", uptime)
        if uptime:
            Uptime.register(self.object, uptime)

    def check_interface_status(self):
        """
        Interface status discovery
        """
        result = self.object.scripts.get_interface_status_ex()
        interfaces = dict(
            (i.name, i)
            for i in Interface.objects.filter(
                managed_object=self.object.id)
        )
        for i in result:
            iface = interfaces.get(i)
            if not iface:
                continue
            kwargs = {
                "interface": i["interface"],
                "admin_status": i.get("admin_status"),
                "oper_status": i.get("oper_status"),
                "full_duplex": i.get("full_duplex"),
                "in_speed": i.get("in_speed"),
                "out_speed": i.get("out_speed"),
                "bandwidth": i.get("bandwidth")                
            }
            changes = self.update_if_changed(
                iface, kwargs,
                ignore_empty=kwargs.keys()
            )
            self.log_changes(
                "[interface_status] Interface %s status has been changed" % i["interface"],
                changes
            )

    def check_mac(self):
        """
        MAC address discovery
        """
        if "get_mac_address_table" not in self.object.scripts:
            self.logger.info(
                "[mac] get_mac_address_table is not supported. Skipping"
            )
            return
        result = self.object.scripts.get_mac_address_table()
        # Populate MACDB
        # @todo: Remove duplicates
        # @todo: Topology discovery
        vc_domain = VCDomain.get_for_object(self.object)
        for v in result:
            if v["type"] != "D" or not v["interfaces"]:
                continue
            iface = self.get_interface(v["interfaces"][0])
            if not iface:
                continue  # Interface not found
            if not iface.profile or not iface.profile.mac_discovery:
                continue  # MAC discovery disabled on interface
            changed = MACDB.submit(
                v["mac"],
                vc_domain,
                v["vlan_id"],
                iface.name
            )
            if changed:
                self.logger.info(
                    "[mac] Interface=%s, VC Domain=%s, VLAN=%s, MAC=%s",
                    iface.name, vc_domain, v["vlan_id"], v["mac"]
                )
