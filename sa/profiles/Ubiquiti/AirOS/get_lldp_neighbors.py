# ---------------------------------------------------------------------
# Ubiquiti.AirOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.snmp.render import render_mac


class Script(BaseScript):
    name = "Ubiquiti.AirOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    OID_CHILDREN_INDEX_MAP = {"mac": 1, "name": 2, "ip": 10}

    def get_lldp_data(self, oid_children_index: int, is_mac: bool = False) -> list:
        """
        get lldp data and return list

        :params:
            oid_children_index - index of the required OID branch,
            is_mac - is the desired OID branch a MAC address
        :return:
            list of data
        """
        result = []

        if is_mac == True:
            for _, value in self.snmp.getnext(
                f"1.3.6.1.4.1.41112.1.4.7.1.{oid_children_index}.1",
                display_hints={f"1.3.6.1.4.1.41112.1.4.7.1.{oid_children_index}.1": render_mac},
            ):
                result.append(value)
        else:
            for _, value in self.snmp.getnext(f"1.3.6.1.4.1.41112.1.4.7.1.{oid_children_index}.1"):
                result.append(value)

        return result

    def execute_snmp(self):

        result, neighbors = {
            "local_interface": "ath0",
            "local_interface_id": self.snmp.get(
                "1.2.840.10036.2.1.1.1.5", display_hints={"1.2.840.10036.2.1.1.1.5": render_mac}
            ),
        }, []

        macs = self.get_lldp_data(self.OID_CHILDREN_INDEX_MAP.get("mac"), is_mac=True)
        names = self.get_lldp_data(self.OID_CHILDREN_INDEX_MAP.get("name"))
        ips = self.get_lldp_data(self.OID_CHILDREN_INDEX_MAP.get("ip"))

        if macs and names and ips:
            for index, _ in enumerate(names):
                neighbors.append(
                    {
                        "remote_chassis_id_subtype": 4,
                        "remote_chassis_id": macs[index],
                        "remote_port_subtype": 5,
                        "remote_port": ips[index],
                        "remote_system_name": names[index],
                    }
                )

        result["neighbors"] = neighbors
        return [result]
