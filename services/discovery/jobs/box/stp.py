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
    # required_capabilities = ["Network | STP"]

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
                if not ri:
                    continue

        # remote object -> [(local, remote), ..]
        candidates = defaultdict(set)
        loops = {}  # first interface, second interface
        # Check local side
        for li, ro, ri in self.iter_neighbors(self.object):
            # Resolve remote object
            remote_object = self.get_neighbor(ro)
            if not remote_object:
                self.logger.debug(
                    "Remote object '%s' is not found. Skipping",
                    ro
                )
                continue
            # Resolve remote interface name
            remote_interface = self.get_remote_interface(
                remote_object,
                ri
            )
            if not remote_interface:
                self.logger.debug(
                    "Cannot resolve remote interface %s:%r. Skipping",
                    remote_object.name, ri
                )
                continue
            # Detecting loops
            if remote_object.id == self.object.id:
                loops[li] = remote_interface
                if (remote_interface in loops and loops[remote_interface] == li):
                    self.logger.debug(
                        "Loop link detected: %s:%s - %s:%s",
                        self.object.name, li,
                        self.object.name, remote_interface)
                    self.confirm_link(
                        self.object, li,
                        remote_object, remote_interface
                    )
                continue
            # Submitting candidates
            self.logger.debug(
                "Link candidate: %s:%s - %s:%s",
                self.object.name, li,
                remote_object.name, remote_interface
            )
            candidates[remote_object].add((li, remote_interface))

        # Checking candidates from remote side
        for remote_object in candidates:
            if (self.required_script and
                    self.required_script not in remote_object.scripts):
                self.logger.debug(
                    "Remote object '%s' does not support %s script. "
                    "Cannot confirm links",
                    remote_object.name
                )
            confirmed = set()
            for li, ro_id, ri in self.iter_neighbors(remote_object):
                ro = self.get_neighbor(ro_id)
                if not ro or ro.id != self.object.id:
                    continue  # To other objects
                remote_interface = self.get_remote_interface(
                    self.object,
                    ri
                )
                if remote_interface:
                    confirmed.add((remote_interface, li))
            for l, r in candidates[remote_object] & confirmed:
                self.confirm_link(
                    self.object, l,
                    remote_object, r
                )
            for l, r in candidates[remote_object] - confirmed:
                self.reject_link(
                    self.object, l,
                    remote_object, r
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
