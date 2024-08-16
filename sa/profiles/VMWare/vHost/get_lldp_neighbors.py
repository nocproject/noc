# ---------------------------------------------------------------------
# VMWare.vHost.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors


class Script(BaseScript):
    name = "VMWare.vHost.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    def execute_controller(self, hid, **kwargs):
        h = self.vim.get_host_by_id(hid)
        hns = h.configManager.networkSystem
        result = []
        if not h.capabilities.supportsNetworkHints:
            return result
        for q in hns.capabilities.supportsNetworkHints.QueryNetworkHint():
            if q.lldpInfo is None:
                continue
            nei = {"remote_port": q.lldpInfo.portId, "remote_chassis_id": q.lldpInfo.chassisId}
            for param in q.lldpInfo.parameter:
                if param.key == "System Name":
                    nei["remote_system_name"] = param.value.strip()
            result += [{
                "local_interface": q.device,
                "neighbors": [nei]
            }]
        return result
