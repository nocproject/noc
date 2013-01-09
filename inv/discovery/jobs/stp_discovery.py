## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## STP Link Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from link_discovery import LinkDiscoveryJob
from noc.settings import config
from noc.inv.models.discoveryid import DiscoveryID


class STPLinkDiscoveryJob(LinkDiscoveryJob):
    """
    Abstract class for link discovery jobs
    """
    name = "stp_discovery"
    map_task = "get_spanning_tree"
    method = "stp"
    ignored = not config.getboolean("stp_discovery", "enabled")
    initial_submit_interval = config.getint("stp_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("stp_discovery",
        "initial_submit_concurrency")
    strict_pending_candidates_check = False

    def process_result(self, object, result):
        self.n_cache = {}  # bridge_id -> object
        self.desg_port_id = {}  # port_id -> name
        for i in result["instances"]:
            for iface in i["interfaces"]:
                if iface["role"] == "designated":
                    # Store designated port id for pending link processing
                    self.desg_port_id[iface["port_id"]] = iface["interface"]
                elif iface["role"] in ("root", "alternate"):
                    # ROOT and ALTERNATE ports are pending check candidates
                    # Get remote object by bridge id
                    remote_object = self.get_neighbor(
                        iface["designated_bridge_id"])
                    if not remote_object:
                        continue
                    # Commit remote port id instead of
                    # interface name.
                    # Will be resolved later in load_pending_checks
                    self.submit_candidate(iface["interface"],
                        remote_object,
                        iface["designated_port_id"])

    def process_pending_checks(self, object):
        for remote_object in self.p_candidates:
            for local_port_id, remote_interface in self.p_candidates[remote_object]:
                local_interface = self.desg_port_id.get(local_port_id)
                if local_interface:
                    self.submit_link(
                        object, local_interface,
                        remote_object, remote_interface)
                    self.submited.add((local_port_id, remote_object, remote_interface))
                else:
                    self.debug("Designated port %s is not found in %s" % (
                        local_port_id, ", ".join(self.desg_port_id.keys())))

    def get_neighbor(self, bridge_id):
        """
        Find neighbor by bridge id
        :param bridge_id:
        :return:
        """
        # Get cached
        n = self.n_cache.get(bridge_id)
        if n:
            return n
        n = DiscoveryID.objects.filter(first_chassis_mac__lte=bridge_id,
            last_chassis_mac__gte=bridge_id).first()
        if n:
            n = n.object
        self.n_cache[bridge_id] = n
        return n
