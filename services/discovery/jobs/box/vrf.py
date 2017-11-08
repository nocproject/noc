# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# VRF discovery
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.ip.models.vrf import VRF
# NOC modules
from noc.services.discovery.jobs.base import DiscoveryCheck


class VRFCheck(DiscoveryCheck):
    """
    VRF discovery
    """
    name = "vrf"
    required_artefacts = ["vrf"]

    def is_enabled(self):
        return (self.object.object_profile.enable_box_discovery_vrf or
                self.object.object_profile.enable_box_discovery_prefix_interface or
                self.object.object_profile.enable_box_discovery_address_interface)

    def handler(self):
        data = self.get_artefact("vrf")
        for name in data:
            v = data[name]
            # Check VRF
            vrf = VRF.get_by_rd(v["rd"])
            if vrf:
                self.logger.info("[%s|%s] Is already exists as \"%s\"",
                                 vrf["name"], vrf["rd"], vrf["name"])
                continue
            # Create VRF
            self.logger.info("[%s|%s] Creating VRF",
                             vrf["name"], vrf["rd"])
            vrf = VRF(
                name=v["name"],
                rd=v["rd"],
                afi_ipv4=True,
                description="Discovered by VRF discovery"
            )
            vrf.save()
