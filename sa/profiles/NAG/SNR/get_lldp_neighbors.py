# ---------------------------------------------------------------------
# NAG.SNR.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_lldp_neighbors import Script as BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.sa.interfaces.base import IntParameter, MACAddressParameter, InterfaceTypeError


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
        re.MULTILINE,
    )

    def execute_cli(self, **kwargs):
        r = []
        # Fallback to CLI
        for lldp in self.cli("show lldp neighbors interface").split("\n\n"):
            match = self.rx_detail.search(lldp)
            if match:
                i = {"local_interface": match.group("local_if"), "neighbors": []}
                n = {"remote_chassis_id_subtype": match.group("rem_cid_type")}
                n["remote_port_subtype"] = {
                    "Interface alias": 1,
                    # "Port component": 2,
                    "MAC address": 3,
                    "Interface": 5,
                    "Local": 7,
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
