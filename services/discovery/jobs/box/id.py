# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ID check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.discoveryid import DiscoveryID
from noc.inv.models.interface import Interface


class IDCheck(DiscoveryCheck):
    """
    Version discovery
    """
    name = "id"
    required_script = "get_discovery_id"

    def handler(self):
        self.logger.info("Checking chassis id")
        result = self.object.scripts.get_discovery_id()
        cm = result.get("chassis_mac")
        if cm:
            cm = ", ".join(
                "%s - %s" % (m["first_chassis_mac"], m["last_chassis_mac"])
                for m in cm if "first_chassis_mac" in m and "last_chassis_mac" in m
            )
        interface_macs = self.get_additional_macs()
        self.logger.info(
            "Identity found: "
            "Chassis MACs = %s, hostname = %s, router-id = %s, "
            "additional MACs = %s",
            cm,
            result.get("hostname"),
            result.get("router_id"),
            ", ".join(interface_macs or [])
        )
        DiscoveryID.submit(
            object=self.object,
            chassis_mac=result.get("chassis_mac"),
            hostname=result.get("hostname"),
            router_id=result.get("router_id"),
            additional_macs=interface_macs
        )

    def get_additional_macs(self):
        """
        Returns list of additional macs
        :return:
        """
        if self.object.object_profile.enable_box_discovery_interface:
            return self.get_macs_from_artefact()
        return self.get_macs_from_interfaces()

    def get_macs_from_artefact(self):
        """
        Return MACs from interface discovery artefact
        :return:
        """
        return self.get_artefact("interface_macs")

    def get_macs_from_interfaces(self):
        """
        Return MACs from collected interfaces
        :return:
        """
        return list(
            set(
                str(d["mac"])
                for d in Interface._get_collection().find({
                    "managed_object": self.object.id,
                    "mac": {
                        "$exists": True
                    }
                }, {
                    "_id": 0,
                    "mac": 1
                }) if d["mac"]
            )
        )
