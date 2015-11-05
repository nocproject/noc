# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MAC Check
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck
from noc.vc.models.vcdomain import VCDomain
from noc.inv.models.macdb import MACDB


class MACCheck(DiscoveryCheck):
    """
    MAC discovery
    """
    name = "mac"
    required_script = "get_mac_address_table"

    def handler(self):
        result = self.object.scripts.get_mac_address_table()
        # Populate MACDB
        # @todo: Remove duplicates
        # @todo: Topology discovery
        vc_domain = VCDomain.get_for_object(self.object)
        for v in result:
            if v["type"] != "D" or not v["interfaces"]:
                continue
            iface = self.get_interface_by_name(v["interfaces"][0])
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
                    "Interface=%s, VC Domain=%s, VLAN=%s, MAC=%s",
                    iface.name, vc_domain, v["vlan_id"], v["mac"]
                )
