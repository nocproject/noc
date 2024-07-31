# ---------------------------------------------------------------------
# Beward.Doorphone.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.snmp.render import render_mac


class Script(BaseScript):
    name = "Beward.Doorphone.get_lldp_neighbors"
    interface = IGetLLDPNeighbors
    cache = True

    def check_timeticks(self, timetick_oid: str = "1.0.8802.1.1.2.1.2.1.0") -> int:
        """
        Get timeticks for collecting lldp.

        :param timetick_oid: oid for collect timetick
        :return: an integer value that is the number of
        timeticks of the last access to the upstream device
        """
        value = self.snmp.get(timetick_oid)
        return value if value else None

    def execute_snmp(self):
        result = {"local_interface": "eth0", "local_interface_id": 1}

        index = self.check_timeticks()
        if not index:
            self.logger.debug(
                "There is no correct index for collecting information of remote device"
            )
            result["neighbors"] = ""
            return [result]

        neighbor = [
            {
                "remote_chassis_id_subtype": self.snmp.get(f"1.0.8802.1.1.2.1.4.1.1.4.{index}.2.4"),
                "remote_chassis_id": self.snmp.get(
                    f"1.0.8802.1.1.2.1.4.1.1.5.{index}.2.4",
                    display_hints={f"1.0.8802.1.1.2.1.4.1.1.5.{index}.2.4": render_mac},
                ),
                "remote_port_subtype": self.snmp.get(
                    f"1.0.8802.1.1.2.1.4.1.1.6.100.2.1.{index}.2.4"
                ),
                "remote_port": self.snmp.get(f"1.0.8802.1.1.2.1.4.1.1.7.{index}.2.4"),
                "remote_system_name": self.snmp.get(f"1.0.8802.1.1.2.1.4.1.1.9.{index}.2.4"),
                "remote_system_description": self.snmp.get(
                    f"1.0.8802.1.1.2.1.4.1.1.10.{index}.2.4"
                ).replace("\n", " "),
            }
        ]

        result["neighbors"] = neighbor

        return [result]
