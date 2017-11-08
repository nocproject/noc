# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NAG.SNR.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import (IntParameter,
                                    MACAddressParameter,
                                    InterfaceTypeError)


class Script(BaseScript):
    name = "NAG.SNR.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_detail = re.compile(
        r"^Port name : (?P<local_if>\S+)\s*\n"
        r"^Port Remote Counter : (?P<status>\S+)\s*\n"
        r"^TimeMark :\S*\n"
        r"^ChassisIdSubtype :(?P<rem_cid_type>.*)\n"
        r"^ChassisId :(?P<id>.*)\n"
        r"^PortIdSubtype :(?P<p_type>.*)\n"
        r"^PortId :(?P<port_id>.*)\n",
        re.MULTILINE
    )

    def execute(self):
        r = []
        """
        # Try SNMP first
        if self.has_snmp():
            try:
                # lldpRemLocalPortNum
                # lldpRemChassisIdSubtype lldpRemChassisId
                # lldpRemPortIdSubtype lldpRemPortId
                # lldpRemSysName lldpRemSysCapEnabled
                for v in self.snmp.get_tables(
                    ["1.0.8802.1.1.2.1.4.1.1.2",
                     "1.0.8802.1.1.2.1.4.1.1.4", "1.0.8802.1.1.2.1.4.1.1.5",
                     "1.0.8802.1.1.2.1.4.1.1.6", "1.0.8802.1.1.2.1.4.1.1.7",
                     "1.0.8802.1.1.2.1.4.1.1.9", "1.0.8802.1.1.2.1.4.1.1.12"
                     ], bulk=True):
                    local_interface = self.snmp.get(
                        "1.3.6.1.2.1.31.1.1.1.1." + v[1], cached=True)
                    remote_chassis_id_subtype = v[2]
                    remotechassisid = ":".join(["%02x" % ord(c) for c in v[3]])
                    remote_port_subtype = v[4]
                    if remote_port_subtype == 7:
                        remote_port_subtype = 5
                    remote_port = v[5]
                    remote_system_name = v[6]
                    remote_capabilities = v[7]

                    i = {"local_interface": local_interface, "neighbors": []}
                    n = {
                        "remote_chassis_id_subtype": remote_chassis_id_subtype,
                        "remote_chassis_id": remotechassisid,
                        "remote_port_subtype": remote_port_subtype,
                        "remote_port": remote_port,
                        "remote_capabilities": remote_capabilities,
                        }
                    if remote_system_name:
                        n["remote_system_name"] = remote_system_name
                    i["neighbors"].append(n)
                    r.append(i)
                return r

            except self.snmp.TimeOutError:
                pass
        """
        # Fallback to CLI
        for lldp in self.cli("show lldp neighbors interface").split("\n\n"):
            match = self.rx_detail.search(lldp)
            if match:
                i = {
                    "local_interface": match.group("local_if"),
                    "neighbors": []
                }
                n = {"remote_chassis_id_subtype": match.group("rem_cid_type")}
                n["remote_port_subtype"] = {
                    # "Interface alias": 1,
                    # "Port component": 2,
                    "MAC address": 3,
                    "Interface": 5,
                    "Local": 7
                }[match.group("p_type")]
                if n["remote_port_subtype"] == 3:
                    remote_port = MACAddressParameter().clean(match.group("port_id"))
                elif n["remote_port_subtype"] == 7:
                    p_id = match.group("port_id")
                    try:
                        remote_port = IntParameter().clean(p_id)
                    except InterfaceTypeError:
                        remote_port = p_id
                else:
                    remote_port = match.group("port_id")
                n["remote_chassis_id"] = match.group("id")
                n["remote_port"] = str(remote_port)
                # Get capability
                cap = 0
                n["remote_capabilities"] = cap
                i["neighbors"] += [n]
                r += [i]
        return r
