## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## REP Link Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from link_discovery import LinkDiscoveryJob
from noc.settings import config


class REPLinkDiscoveryJob(LinkDiscoveryJob):
    """
    REP Link Discovery
    """
    name = "rep_discovery"
    map_task = "get_rep_topology"
    method = "rep"
    ignored = not config.getboolean("rep_discovery", "enabled")
    initial_submit_interval = config.getint("rep_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("rep_discovery",
        "initial_submit_concurrency")

    def process_result(self, object, result):
        for segment in result:
            topology = segment["topology"]
            # Find own ports
            o = [i for i, p in enumerate(topology)
                 if self.is_own_mac(p["mac"])]
            if not o:
                continue  # Not found
            elif len(o) == 2:
                f, s = o
                L = len(topology)
                if not topology[f]["edge_no_neighbor"]:
                    self.submit_pair(
                        object, topology[f], topology[(f - 1) % L])
                if not topology[s]["edge_no_neighbor"]:
                    self.submit_pair(
                        object, topology[s], topology[(s + 1) % L])
            else:
                # Something strange
                self.error("Invalid REP discovery result: %r" % topology)
                continue

    def submit_pair(self, object, local_info, remote_info):
        remote_object = self.get_neighbor_by_mac(remote_info["mac"])
        if not remote_object:
            return  # Not found still
        self.submit_candidate(
            object.profile.convert_interface_name(local_info["port"]),
            remote_object,
            remote_object.profile.convert_interface_name(remote_info["port"])
        )
