# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ID check
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.inv.models.discoveryid import DiscoveryID


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
                for m in cm
            )
        self.logger.info(
            "Identity found: "
            "Chassis MACs = %s, hostname = %s, router-id = %s",
            cm,
            result.get("hostname"),
            result.get("router_id")
        )
        DiscoveryID.submit(
            object=self.object,
            chassis_mac=result.get("chassis_mac"),
            hostname=result.get("hostname"),
            router_id=result.get("router_id")
        )
