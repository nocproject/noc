# ---------------------------------------------------------------------
# STP check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck
from noc.core.error import NOCError


class STPCheck(TopologyDiscoveryCheck):
    """
    STP Topology discovery
    """

    name = "stp"
    required_script = "get_spanning_tree"
    required_capabilities = ["Network | STP"]

    def handler(self):
        self.logger.info("Checking %s topology", self.name)
        roots = self.cached_neighbors(
            self.object, "mo-neighbors-stp-root-%s" % self.object.id, self.get_root_ports
        )
        for ro in roots:
            remote_object = self.get_neighbor(ro)
            if not remote_object:
                self.logger.debug("Remote object '%s' is not found. Skipping", ro)
                continue
            rdmap = self.cached_neighbors(
                remote_object,
                "mo-neighbors-stp-desg-%s" % remote_object.id,
                self.get_designated_ports,
            )
            for li, rpid in roots[ro]:
                ri = rdmap.get(rpid)
                if ri:
                    # Link found
                    self.confirm_link(self.object, li, remote_object, ri)

    def get_root_ports(self, mo):
        """
        Returns a dict of
        remote_object_id -> set((local_interface, remote_port_id)
        """
        result = mo.scripts.get_spanning_tree()
        roots = defaultdict(set)  # Neighbor -> [(local iface, remote_id)]
        for i in result["instances"]:
            for iface in i["interfaces"]:
                if iface["role"] in ("root", "alternate"):
                    roots[iface["designated_bridge_id"]].add(
                        (iface["interface"], self.convert_port_id(iface["designated_port_id"]))
                    )
        roots = {ro: list(roots[ro]) for ro in roots}
        self.logger.debug("Roots ports: %s" % roots)
        return roots

    def get_designated_ports(self, ro):
        """
        Returns a dict of designated port_id -> name
        """
        dmap = {}
        if self.required_script not in ro.scripts:
            self.logger.info(
                "Remote object '%s' does not support %s script. " "Cannot confirm links",
                ro.name,
                self.required_script,
            )
            return dmap
        try:
            result = ro.scripts.get_spanning_tree()
        except NOCError as e:
            self.logger.error("Cannot get neighbors from candidate %s: %s", ro.name, e)
            self.set_problem(
                # path=list(candidates[remote_object])[0][0],
                message="Cannot get neighbors from candidate %s: %s" % (ro.name, e)
            )
            return dmap
        for i in result["instances"]:
            for iface in i["interfaces"]:
                if iface["role"] == "designated":
                    pi = self.convert_port_id(iface["port_id"])
                    dmap[pi] = iface["interface"]
        self.logger.debug("Designate port map %s" % dmap)
        return dmap

    get_neighbor = TopologyDiscoveryCheck.get_neighbor_by_mac

    @staticmethod
    def convert_port_id(port_id):
        left, right = [int(x) for x in port_id.split(".")]
        left //= 16
        return "%x" % ((left << 12) + right)
