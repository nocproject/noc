# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC Modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.lldp import (
    LLDP_CHASSIS_SUBTYPE_MAC,
    LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS,
    LLDP_PORT_SUBTYPE_NAME,
    LLDP_CAP_OTHER,
    LLDP_CAP_REPEATER,
    LLDP_CAP_BRIDGE,
    LLDP_CAP_WLAN_ACCESS_POINT,
    LLDP_CAP_ROUTER,
    LLDP_CAP_TELEPHONE,
    lldp_caps_to_bits,
)


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    def get_local_iface(self):
        r = {}
        ports = super().get_local_iface()
        for port, li in ports.items():
            iftype = self.profile.get_interface_type(li["local_interface"])
            if iftype == "SVI":
                continue
            r[port] = li
        return r

    def execute_cli(self):
        res = []
        interfaces = []
        for n, f, r in self.cli_detail('/interface print detail without-paging where type="ether"'):
            interfaces += [r["name"]]
        self.logger.debug("Collected interfaces: %s", interfaces)
        for n, f, r in self.cli_detail("/ip neighbor print detail without-paging"):
            # For LACP based link
            local_iface, *ifaces = r["interface"].split(",")
            if local_iface not in interfaces:
                self.logger.debug("[%s] Local iface not in interface table.", local_iface)
                continue
            if "discovered-by" in r and "lldp" not in r["discovered-by"]:
                self.logger.debug("[%s] Not LLDP discovered neighbor", local_iface)
                continue
            if r.get("mac-address"):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
                chassis_id = r["mac-address"]
            elif r.get("address4"):
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
                chassis_id = r["address4"]
            else:
                self.logger.debug("[%s] Unknown identity", local_iface)
                continue
            if r.get("interface-name"):
                port_subtype = LLDP_PORT_SUBTYPE_NAME
                port = r["interface-name"]
                port = port.strip(" \x00")
            else:
                continue
            caps = lldp_caps_to_bits(
                r["system-caps"].strip().split(","),
                {
                    "other": LLDP_CAP_OTHER,
                    "repeater": LLDP_CAP_REPEATER,
                    "bridge": LLDP_CAP_BRIDGE,
                    "wlan-ap": LLDP_CAP_WLAN_ACCESS_POINT,
                    "router": LLDP_CAP_ROUTER,
                    "telephone": LLDP_CAP_TELEPHONE,
                    # "": LLDP_CAP_DOCSIS_CABLE_DEVICE,
                    # "": LLDP_CAP_STATION_ONLY,  # S-VLAN
                },
            )
            interface = {
                "local_interface": local_iface,
                "neighbors": [
                    {
                        "remote_chassis_id_subtype": chassis_id_subtype,
                        "remote_chassis_id": chassis_id,
                        "remote_port_subtype": port_subtype,
                        "remote_port": port,
                        "remote_capabilities": caps,
                    }
                ],
            }
            if r.get("address4"):
                interface["neighbors"][0]["remote_mgmt_address"] = r["address4"]
            if "system-description" in r:
                interface["neighbors"][0]["remote_system_description"] = r[
                    "system-description"
                ].strip(" \x00")
            res += [interface]
        return res
