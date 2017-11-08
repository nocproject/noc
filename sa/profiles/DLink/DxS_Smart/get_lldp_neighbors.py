# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS_Smart.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetLLDPNeighbors


class Script(noc.sa.script.Script):
    name = "DLink.DxS_Smart.get_lldp_neighbors"
    implements = [IGetLLDPNeighbors]

    def execute(self):
        r = []
        n = {}
        per_port = {}
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for oid, v in self.snmp.get_tables(
                        ["1.0.8802.1.1.2.1.4.1.1"], bulk=True):
                    (seq, timemark, local_port, rem_index) = oid.split(".")
                    if not n.get(rem_index):
                        n[rem_index] = {}
                        per_port.setdefault(local_port, []).append(n[rem_index])
                    if seq == "4":  # lldpRemChassisIdSubtype
                        n[rem_index]["remote_chassis_id_subtype"] = v
                    if seq == "5":  # lldpRemChassisId
                        n[rem_index]["remote_chassis_id"] = v
                    if seq == "6":  # lldpRemPortIdSubtype
                        n[rem_index]["remote_port_subtype"] = v
                    if seq == "7":  # lldpRemPortId
                        n[rem_index]["remote_port"] = re.split("[:/]", v)[-1]
                    if seq == "9":  # lldpRemSysName
                        n[rem_index]["remote_system_name"] = v

            except self.snmp.TimeOutError:
                pass
            for port, nbs in per_port.items():
                r.append({"local_interface": port, "neighbors": nbs})
        return r
