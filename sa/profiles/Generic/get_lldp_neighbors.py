# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
# from noc.core.mib import mib
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Generic.get_lldp_neighbors"
    cache = True
    interface = IGetLLDPNeighbors

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
                local_ports[v[0]] = {"local_interface": v[3],
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
