# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Generic.get_topology_data
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetipdiscovery import IGetIPDiscovery


class Script(BaseScript):
=======
##----------------------------------------------------------------------
## Generic.get_topology_data
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetIPDiscovery, IGetARP


class Script(NOCScript):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Retrieve data for IP discovery
    """
    name = "Generic.get_ip_discovery"
<<<<<<< HEAD
    interface = IGetIPDiscovery
    requires = ["get_arp"]
=======
    implements = [IGetIPDiscovery]
    requires = []
    requires = [("get_arp", IGetARP)]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    def execute(self):
        # Prepare VRFs
        vrfs = {
            "default": {
                "name": "default",
                "addresses": []
            }
        }
<<<<<<< HEAD
        if "get_mpls_vpn" in self.scripts:
=======
        if self.scripts.has_script("get_mpls_vpn"):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                r = self.scripts.get_mpls_vpn()
            except self.CLISyntaxError:
                r = []
            for v in r:
                if v["status"] and v["type"] == "VRF":
                    vrf = {
                        "name": v["name"],
                        "addresses": []
                    }
                    if "rd" in v:
                        vrf["rd"] = v["rd"]
                    vrfs[v["name"]] = vrf
        # Get IPv6 neighbors (global?)
<<<<<<< HEAD
        if "get_ipv6_neighbor" in self.scripts:
=======
        if self.scripts.has_script("get_ipv6_neighbor"):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                r = self.scripts.get_ipv6_neighbor()
            except self.CLISyntaxError:
                r = []
            if r:
                vrfs["default"]["addresses"] += [{
                    "ip": x["ip"],
                    "afi": "6",
                    "mac": x["mac"],
                    "interface": x["interface"]}
                for x in r if x["state"] == "reachable"
                ]
        # Iterate through VRF
        data = []
        for v in vrfs:
            a = []
            vrf = None if v == "default" else v
            # Process ARP cache
            arp_cache = self.scripts.get_arp(vrf=vrf)
            a += [{
                "ip": x["ip"],
                "afi": "4",
                "mac": x["mac"],
                "interface": x["interface"]
            } for x in arp_cache if "mac" in x and x["mac"]]
            # Process NBD
            vd = vrfs[v].copy()
            vd["addresses"] += a
            data += [vd]
        # Return collected data
        return data
