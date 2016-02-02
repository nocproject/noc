# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## STP check
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck


class STPCheck(TopologyDiscoveryCheck):
    """
    STP Topology discovery
    """
    name = "stp"
    required_script = "get_spanning_tree"
    required_capabilities = ["Network | STP"]

    def handler(self):
        self.logger.info("Checking %s topology", self.name)
        roots = self.get_root_ports()
        for ro in roots:
            remote_object = self.get_neighbor(ro)
            if not remote_object:
                self.logger.debug(
                    "Remote object '%s' is not found. Skipping",
                    ro
                )
                continue
            rdmap = self.get_designated_ports(remote_object)
            for li, rpid in roots[ro]:
                ri = rdmap.get(rpid)
                if ri:
                    # Link found
                    self.confirm_link(
                        self.object, li,
                        remote_object, ri
                    )

    def get_root_ports(self):
        """
        Returns a dict of
        remote_object_id -> set((local_interface, remote_port_id)
        """
        result = self.object.scripts.get_spanning_tree()
        roots = defaultdict(set)  # Neighbor -> [(local iface, remote_id)]
        for i in result["instances"]:
            for iface in i["interfaces"]:
                if iface["role"] in ("root", "alternate"):
                    roots[iface["designated_bridge_id"]].add((
                        iface["interface"],
                        self.convert_port_id(
                            iface["designated_port_id"]
                        )
                    ))
        return roots

    def get_designated_ports(self, ro):
        """
        Returns a dict of designated port_id -> name
        """
        dmap = {}
        result = ro.scripts.get_spanning_tree()
        for i in result["instances"]:
            for iface in i["interfaces"]:
                if iface["role"] == "designated":
                    pi = self.convert_port_id(iface["port_id"])
                    dmap[pi] = iface["interface"]
        return dmap

    get_neighbor = TopologyDiscoveryCheck.get_neighbor_by_mac

    @staticmethod
    def convert_port_id(port_id):
        l, r = [int(x) for x in port_id.split(".")]
        l //= 16
        return "%x" % ((l << 12) + r)
