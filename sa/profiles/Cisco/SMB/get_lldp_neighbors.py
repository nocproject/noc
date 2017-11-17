# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.SMB.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Cisco.SMB.get_lldp_neighbors"
    cache = True
    interface = IGetLLDPNeighbors

    def execute_snmp(self):
        neighb = ("remote_chassis_id_subtype",
		  "remote_chassis_id",
		  "remote_port_subtype",
                  "remote_port",
		  "remote_port_description",
		  "remote_system_name")
        r = []
        local_ports = {}
        if self.has_snmp():
            # Get LocalPort Table
            for v in self.snmp.get_tables(["1.0.8802.1.1.2.1.3.7.1.1",
                                           "1.0.8802.1.1.2.1.3.7.1.2",
                                           "1.0.8802.1.1.2.1.3.7.1.3",
                                           "1.0.8802.1.1.2.1.3.7.1.4"]):
		if v[2] == 3:
		    v[3] = ":".join(["%02x" % ord(c) for c in v[3]])
                local_ports[v[0]] = {"local_interface": v[3],
                                     "local_interface_subtype": v[2]}

            for v in self.snmp.get_tables(["1.0.8802.1.1.2.1.4.1.1.2",
                                           "1.0.8802.1.1.2.1.4.1.1.4",
                                           "1.0.8802.1.1.2.1.4.1.1.5",
                                           "1.0.8802.1.1.2.1.4.1.1.6",
                                           "1.0.8802.1.1.2.1.4.1.1.7",
                                           "1.0.8802.1.1.2.1.4.1.1.8",
                                           "1.0.8802.1.1.2.1.4.1.1.9",
                                           ], bulk=True):
                if v[7]:
                    neigh = dict(zip(neighb, v[2:]))
                    if neigh["remote_chassis_id_subtype"] == 4:
                        neigh["remote_chassis_id"] = MAC(":".join(["%02x" % ord(c) for c in v[3]]))
		    v[5] = v[5].rstrip("\x00")
		    if neigh["remote_port_subtype"] == 3:
		        neigh["remote_port"] = ":".join(["%02x" % ord(c) for c in v[5]])
		    v[7] = v[7].rstrip("\x00")
		    neigh["remote_capabilities"] = (["%02x" % ord(x) for x in v[7]])[0]
                    r += [{
                        "local_interface": local_ports[v[0].split(".")[1]]["local_interface"],
                        "neighbors": [neigh]
                    }]
        return r
