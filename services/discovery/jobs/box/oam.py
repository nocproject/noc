# ---------------------------------------------------------------------
# OAM check
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import defaultdict

# NOC modules
from noc.services.discovery.jobs.base import TopologyDiscoveryCheck
from noc.core.mac import MAC
from noc.inv.models.macblacklist import MACBlacklist


class OAMCheck(TopologyDiscoveryCheck):
    """
    OAM Topology discovery
    """

    name = "oam"
    required_script = "get_oam_status"
    required_capabilities = ["Network | OAM"]

    def iter_neighbors(self, mo):
        result = mo.scripts.get_oam_status()
        # Build mac to interfaces map
        remote_macs = defaultdict(list)  # remote mac -> local iface
        for n in result:
            if "L" in n["caps"]:
                remote_mac = n["interface"]
                if MACBlacklist.is_banned_mac(remote_mac, is_duplicated=True):
                    self.logger.info("Banned MAC %s found. Skipping", remote_mac)
                elif MAC(remote_mac).is_multicast:
                    self.logger.info("MAC address %s is multicast. Skipping", remote_mac)
                else:
                    remote_macs[n["remote_mac"]] += [remote_mac]
        # Resolve links
        for rmac in remote_macs:
            if len(remote_macs[rmac]) == 1:
                local_interface = remote_macs[rmac][0]
                # Try to find interface by
                mo = self.get_neighbor_by_mac(rmac)
                remote_interface = self.get_interface_by_mac(mac=rmac, mo=mo)
                if remote_interface:
                    yield local_interface, remote_interface.managed_object.id, remote_interface.name

    get_neighbor = TopologyDiscoveryCheck.get_neighbor_by_id
