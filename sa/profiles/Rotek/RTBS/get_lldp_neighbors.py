# ---------------------------------------------------------------------
# Rotek.RTBS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Tuple, List

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.snmp.render import render_mac


class Script(BaseScript):
    name = "Rotek.RTBS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    def get_remote_devices_info(
        self, base_oid: str = "1.3.6.1.4.1.41752.3.5.1.3.2.1"
    ) -> Tuple[List[str]]:
        """
        Get remote devices information: MAC-addresses and ports

        :param base_oid: - the parent OID for the data request
        :returns: a tuple containing lists of MAC addresses and ports
        """
        for index in range(1, 3):
            if index == 1:
                macs = [
                    mac
                    for _, mac in self.snmp.getnext(
                        f"{base_oid}.{str(index)}.8.6",
                        display_hints={f"{base_oid}.{str(index)}.8.6": render_mac},
                    )
                ]
            else:
                ports = [str(port) for _, port in self.snmp.getnext(f"{base_oid}.{str(index)}")]

        return macs, ports

    def execute_snmp(self):

        result, neighbors = {
            "local_interface": self.snmp.get("1.3.6.1.4.1.41752.3.5.1.2.1.1.4.8"),
            "local_interface_id": self.snmp.get(
                "1.3.6.1.4.1.41752.3.5.1.2.1.1.5.8",
                display_hints={"1.3.6.1.4.1.41752.3.5.1.2.1.1.5.8": render_mac},
            ),
        }, []

        macs, ports = self.get_remote_devices_info()

        for index in range(len(macs)):
            neighbors.append(
                {
                    "remote_chassis_id_subtype": 4,
                    "remote_chassis_id": macs[index],
                    "remote_port_subtype": 5,
                    "remote_port": ports[index],
                }
            )

        result["neighbors"] = neighbors
        return [result]
