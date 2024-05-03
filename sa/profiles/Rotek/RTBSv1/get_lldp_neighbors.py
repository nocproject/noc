# ---------------------------------------------------------------------
# Rotek.RTBSv1.get_lldp_neighbors
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
    name = "Rotek.RTBSv1.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    def get_remote_ports_data(
        self,
        ports: dict = None,
        base_oid_start: str = "1.3.6.1.4.1.41752.3.10.1.3.2.1",
        base_oid_end: str = "6.236.76.77.86",
    ) -> List[str]:
        """
        Get port description: Tx-packets, Rx-packets, signal and noise levels

        :param ports: dict of ports;
        :param base_oid_start: base oid start
        :param base_oid_end: base oid end
            between start and end needs oid index
        :returns: a list of port description
        """

        if ports is None:
            ports = {}

        description_map, ports_description = {
            "TxBytes": "3",
            "RxBytes": "4",
            "Signal Level": "5",
            "Noise Level": "6",
        }, []

        for device_index in ports.keys():
            result = []
            for descr_name, oid_index in description_map.items():
                response = self.snmp.get(
                    f"{base_oid_start}.{oid_index}.{base_oid_end}.{device_index}"
                )
                result.append(
                    f"{descr_name}: {response}" + " bytes"
                    if oid_index in ("3", "4")
                    else f"{descr_name}: {response}" + " dBm"
                )
            ports_description.append(", ".join(result))

        return ports_description

    def get_remote_devices_info(
        self, base_oid: str = "1.3.6.1.4.1.41752.3.10.1.3.2.1"
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
                        f"{base_oid}.{str(index)}",
                        display_hints={f"{base_oid}.{str(index)}": render_mac},
                    )
                ]
            else:
                ports = {
                    ".".join(reversed(oid.split(".")[-1:-3:-1])): str(port)
                    for oid, port in self.snmp.getnext(f"{base_oid}.{str(index)}")
                }

        port_description = self.get_remote_ports_data(ports=ports)

        return macs, list(ports.values()), port_description

    def execute_snmp(self):

        result, neighbors = {
            "local_interface": "ath0",
            "local_interface_id": self.snmp.get(
                "1.3.6.1.4.1.41752.3.10.1.2.1.1.1.6",
                display_hints={"1.3.6.1.4.1.41752.3.10.1.2.1.1.1.6": render_mac},
            ),
        }, []

        macs, ports, ports_description = self.get_remote_devices_info()

        for index in range(len(macs)):
            neighbors.append(
                {
                    "remote_chassis_id_subtype": 4,
                    "remote_chassis_id": macs[index],
                    "remote_port_subtype": 5,
                    "remote_port": ports[index],
                    "remote_port_description": ports_description[index],
                }
            )

        result["neighbors"] = neighbors
        return [result]
