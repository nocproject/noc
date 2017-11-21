# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.SMB.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import struct

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import MACAddressParameter, IPv4Parameter


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
            for v in self.snmp.get_tables(["1.0.8802.1.1.2.1.3.7.1.2",
                                           "1.0.8802.1.1.2.1.3.7.1.3",
                                           "1.0.8802.1.1.2.1.3.7.1.4"]):
		if v[1] == 3:
		    v[2] = MACAddressParameter().clean(v[2])
                local_ports[v[0]] = {"local_interface": v[2],
                                     "local_interface_subtype": v[1]}

            for v in self.snmp.get_tables(["1.0.8802.1.1.2.1.4.1.1.4",
                                           "1.0.8802.1.1.2.1.4.1.1.5",
                                           "1.0.8802.1.1.2.1.4.1.1.6",
                                           "1.0.8802.1.1.2.1.4.1.1.7",
                                           "1.0.8802.1.1.2.1.4.1.1.8",
                                           "1.0.8802.1.1.2.1.4.1.1.9",
					   "1.0.8802.1.1.2.1.4.1.1.12"
                                           ], bulk=True):
                if v[6]:
                    neigh = dict(zip(neighb, v[1:]))
		    if neigh["remote_chassis_id_subtype"] == 4:
			neigh["remote_chassis_id"] = MACAddressParameter().clean(v[2])

		    if neigh["remote_port_subtype"] == 4:
			neigh["remote_port"] = IPv4Parameter().clean(v[4])
	            elif neigh["remote_port_subtype"] == 3:
        		neigh["remote_port"] = MACAddressParameter().clean(v[4])
		    else:
			neigh["remote_port"] = v[4].rstrip("\x00")
		    neigh["remote_system_name"] = v[6].rstrip("\x00")
		    neigh["remote_capabilities"] = (struct.unpack("h", v[7])[0])
                    r += [{
                        "local_interface": local_ports[v[0].split(".")[1]]["local_interface"],
                        "neighbors": [neigh]
                    }]
        return r
