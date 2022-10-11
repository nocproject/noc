# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
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

    def execute(self):
        res = []
        interfaces = []
        for n, f, r in self.cli_detail('/interface print detail without-paging where type="ether"'):
            interfaces += [r["name"]]
        for n, f, r in self.cli_detail("/ip neighbor print detail without-paging"):
            if "system-caps" not in r or r["system-caps"] == "":
                continue
            if r["interface"] not in interfaces:
                continue
            if "address4" in r and "address4" != "":
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_NETWORK_ADDRESS
                chassis_id = r["address4"]
            elif "mac-address" in r and "mac-address" != "":
                chassis_id_subtype = LLDP_CHASSIS_SUBTYPE_MAC
                chassis_id = r["mac-address"]
            else:
                raise self.NotSupportedError()
            if "interface-name" in r and "interface-name" != "":
                port_subtype = LLDP_PORT_SUBTYPE_NAME
                port = r["interface-name"]
                port = port.strip(" \x00")
            else:
                raise self.NotSupportedError()
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
                "local_interface": r["interface"],
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
            if "system-description" in r:
                interface["neighbors"][0]["remote_system_description"] = r[
                    "system-description"
                ].strip(" \x00")
            res += [interface]
        return res
