# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Generic.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
# from noc.core.mib import mib
from noc.core.mac import MAC
from noc.core.mib import mib


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
            for v in self.snmp.get_tables([mib["LLDP-MIB::lldpLocPortNum"],
                                           mib["LLDP-MIB::lldpLocPortIdSubtype"],
                                           mib["LLDP-MIB::lldpLocPortId"],
                                           mib["LLDP-MIB::lldpLocPortDesc"]]):
                local_ports[v[0]] = {"local_interface": v[3],
                                     "local_interface_subtype": v[2]}

            for v in self.snmp.get_tables([mib["LLDP-MIB::lldpRemLocalPortNum"],
                                           mib["LLDP-MIB::lldpRemChassisIdSubtype"],
                                           mib["LLDP-MIB::lldpRemChassisId"],
                                           mib["LLDP-MIB::lldpRemPortIdSubtype"],
                                           mib["LLDP-MIB::lldpRemPortId"],
                                           mib["LLDP-MIB::lldpRemPortDesc"],
                                           mib["LLDP-MIB::lldpRemSysName"]
                                           ], bulk=True):
                if v:
                    neigh = dict(zip(neighb, v[2:]))
                    # cleaning
                    neigh["remote_port"] = neigh["remote_port"].strip(" \x00")  # \x00 Found on some devices
                    if neigh["remote_chassis_id_subtype"] == 4:
                        neigh["remote_chassis_id"] = \
                            MAC(neigh["remote_chassis_id"])
                    if neigh["remote_port_subtype"] == 3:
                        try:
                            neigh["remote_port"] = MAC(neigh["remote_port"])
                        except ValueError:
                            self.logger.warning("Bad MAC address on Remote Neighbor: %s", neigh["remote_port"])
                    r += [{
                        "local_interface": local_ports[v[0].split(".")[1]]["local_interface"],
                        # @todo if local interface subtype != 5
                        # "local_interface_id": 5,
                        "neighbors": [neigh]
                    }]
        return r
