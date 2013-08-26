## -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OAM Link Discovery Job
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## NOC modules
from link_discovery import LinkDiscoveryJob
from noc.inv.models.interface import Interface
from noc.settings import config


class OAMLinkDiscoveryJob(LinkDiscoveryJob):
    """
    OAM Link Discovery
    """
    name = "oam_discovery"
    map_task = "get_oam_status"
    method = "rep"
    ignored = not config.getboolean("oam_discovery", "enabled")
    initial_submit_interval = config.getint("oam_discovery",
        "initial_submit_interval")
    initial_submit_concurrency = config.getint("oam_discovery",
        "initial_submit_concurrency")

    def process_result(self, object, result):
        # Build mac to interfaces map
        remote_macs = defaultdict(list)  # remote mac -> local iface
        for n in result:
            if "L" in n["caps"]:
                remote_macs[n["remote_mac"]] += [n["interfaces"]]
        # Resolve links
        for rmac in remote_macs:
            if len(remote_macs[rmac]) == 1:
                local_interface = remote_macs[rmac][0]
                # Try to find interface by mac
                il = list(Interface.objects.filter(mac=rmac))
                if len(il) == 1:
                    # Exact match by mac found
                    remote_interface = il[0]
                    self.submit_candidate(
                        local_interface=local_interface,
                        remote_object=remote_interface.managed_object,
                        remote_interface=remote_interface.name
                    )
