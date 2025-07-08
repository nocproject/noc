# ---------------------------------------------------------------------
# ID check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.discoveryid import DiscoveryID, MACRange


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
        chassis_mac = (
            [MACRange(first_mac=m["first_chassis_mac"], last_mac=m["last_chassis_mac"]) for m in cm]
            if cm
            else None
        )
        interface_macs = self.get_artefact("interface_macs")
        self.logger.info(
            "Identity found: "
            "Chassis MACs = %s, hostname = %s, router-id = %s, "
            "additional MACs = %s",
            ", ".join(str(r) for r in chassis_mac) if chassis_mac else "None",
            result.get("hostname"),
            result.get("router_id"),
            ", ".join(interface_macs or []),
        )
        try:
            DiscoveryID.submit(
                object=self.object,
                chassis_mac=chassis_mac,
                hostname=result.get("hostname"),
                router_id=result.get("router_id"),
                additional_macs=interface_macs,
            )
        except ValueError as e:
            self.logger.error("Error when saved Identity: '%s'", e)
