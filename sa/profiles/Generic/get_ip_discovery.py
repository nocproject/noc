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
    """
    Retrieve data for IP discovery
    """

    name = "Generic.get_ip_discovery"
    interface = IGetIPDiscovery
    requires = ["get_arp"]

    def execute(self):
        # Prepare VRFs
        vrfs = {"default": {"name": "default", "addresses": []}}
        vrf_iface_map = {}
        if "get_mpls_vpn" in self.scripts:
            try:
                r = self.scripts.get_mpls_vpn()
            except (self.CLISyntaxError, self.NotSupportedError):
                r = []
            for v in r:
                if v["status"] and v["type"].lower() == "vrf":
                    vrf = {"name": v["name"], "addresses": [], "interfaces": []}
                    if "rd" in v:
                        vrf["rd"] = v["rd"]
                    if "vpn_id" in v:
                        vrf["vpn_id"] = v["vpn_id"]
                    vrf["interfaces"] = v["interfaces"]
                    for i in v["interfaces"]:
                        vrf_iface_map[i] = v["name"]
                    vrfs[v["name"]] = vrf
        # Get IPv6 neighbors (global?)
        if "get_ipv6_neighbor" in self.scripts:
            try:
                r = self.scripts.get_ipv6_neighbor()
            except (self.CLISyntaxError, self.NotSupportedError):
                r = []
            if r:
                for x in r:
                    if x["state"] != "reachable":
                        continue
                    vrf = vrf_iface_map.get(x["interface"], "default")
                    vrfs[vrf]["addresses"] += [
                        {"ip": x["ip"], "afi": "6", "mac": x["mac"], "interface": x["interface"]}
                    ]
        # Iterate through VRF
        data = []
        for v in vrfs:
            a = []
            vrf = None if v == "default" else v
            # Process ARP cache
            arp_cache = self.scripts.get_arp(vrf=vrf)
            for x in arp_cache:
                if not x.get("mac"):
                    continue
                if vrf and x["interface"] not in vrfs[v]["interfaces"]:
                    continue
                if not vrf and x["interface"] in vrf_iface_map:
                    continue
                a += [{"ip": x["ip"], "afi": "4", "mac": x["mac"], "interface": x["interface"]}]
            # Process NBD
            vd = vrfs[v].copy()
            vd["addresses"] += a
            data += [vd]
        # Return collected data
        return data
