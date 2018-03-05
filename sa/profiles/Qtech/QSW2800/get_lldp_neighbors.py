# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Qtech.QSW2800.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_int = re.compile(r"^Port name\s+:\s+(?P<interface>.+)\n"
                        r"Port Remote Counter\s+:\s+(?P<count>\d+)\n"
                        r"TimeMark\s+:\d+\n"
                        r"ChassisIdSubtype\s+:(?P<chassis_subtype>\d+)\n"
                        r"ChassisId\s+:(?P<chassis_id>.+)\n"
                        r"PortIdSubtype\s+:(?P<port_subtype>.+)\n"
                        r"PortId\s+:(?P<port_id>.+)\n",
                        re.MULTILINE)

    rx_mac = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$")

    def execute_snmp(self):
        neighb = (
            "remote_chassis_id_subtype", "remote_chassis_id",
            "remote_port_subtype", "remote_port",
            "remote_port_description", "remote_system_name"
        )
        r = []
        local_ports = {}
        if self.has_snmp():
            # Get LocalPort Table
            for v in self.snmp.get_tables(["1.0.8802.1.1.2.1.3.7.1.1",
                                           "1.0.8802.1.1.2.1.3.7.1.2",
                                           "1.0.8802.1.1.2.1.3.7.1.3",
                                           "1.0.8802.1.1.2.1.3.7.1.4"]):

                local_ports[v[0]] = {"local_interface": v[4],
                                     "local_interface_subtype": v[2]}

            for v in self.snmp.get_tables(["1.0.8802.1.1.2.1.4.1.1.2",
                                           "1.0.8802.1.1.2.1.4.1.1.4",
                                           "1.0.8802.1.1.2.1.4.1.1.5",
                                           "1.0.8802.1.1.2.1.4.1.1.6",
                                           "1.0.8802.1.1.2.1.4.1.1.7",
                                           "1.0.8802.1.1.2.1.4.1.1.8",
                                           "1.0.8802.1.1.2.1.4.1.1.9"
                                           ], bulk=True):
                if v:
                    neigh = dict(zip(neighb, v[2:]))
                    if neigh["remote_chassis_id_subtype"] == 4:
                        neigh["remote_chassis_id"] = \
                            MAC(neigh["remote_chassis_id"])
                    if neigh["remote_port_subtype"] == 3:
                        neigh["remote_port"] = MAC(neigh["remote_port"])
                    r += [{
                        "local_interface": local_ports[v[0].split(".")[1]]["local_interface"],
                        # @todo if local interface subtype != 5
                        # "local_interface_id": 5,
                        "neighbors": [neigh]
                    }]
        return r

    def execute_cli(self):
        result = []
        try:
            lldp = self.cli("show lldp neighbors interface")
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        for match in self.rx_int.finditer(lldp):
            if match.group("count") == 0:
                continue
            result += [{
                "local_interface": match.group("interface"),
                "neighbors": [{
                    "remote_chassis_id_subtype": match.group("chassis_subtype"),
                    "remote_chassis_id": match.group("chassis_id"),
                    "remote_port_subtype": {
                        "Interface alias": 1,
                        "Port component": 2,
                        "Local": 7,
                        "Interface": 5,
                        "MAC address": 3
                    }[match.group("port_subtype")],
                    "remote_port": match.group("port_id")
                }]
            }]
        return result
