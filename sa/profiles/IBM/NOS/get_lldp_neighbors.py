# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IBM.NOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlldpneighbors import IGetLLDPNeighbors
from noc.core.validators import is_int, is_ipv4
from noc.sa.interfaces.base import MACAddressParameter


class Script(BaseScript):
    name = "IBM.NOS.get_lldp_neighbors"
    interface = IGetLLDPNeighbors

    rx_lldp = re.compile(
        r"^(?P<local_port>\S+)\s+\|\s+\d+\s+\|\s+(?P<remote_id>\S+|.{17})"
        r"\s+\|\s(?P<remote_port>\S+)\s+\|\s+(?P<remote_n>\S+)\s*\|",
        re.MULTILINE,
    )

    rx_mac = re.compile(r"(?:(?:\d|\w){2}[\-\s\:]){5}(?:\d|\w){2}")

    def execute_cli(self):
        r = []
        try:
            v = self.cli("show lldp remote-device | begin LocalPort")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        if v:
            for match in self.rx_lldp.finditer(v):
                local_port = match.group("local_port")
                remote_chassis_id = match.group("remote_id")
                remote_chassis_id_subtype = 4
                remote_port = match.group("remote_port")
                rn = match.group("remote_n")
                remote_port_subtype = 5
                if self.rx_mac.match(remote_port):
                    remote_port = MACAddressParameter().clean(remote_port)
                    remote_port_subtype = 3
                elif is_ipv4(remote_port):
                    remote_port_subtype = 4
                elif is_int(remote_port):
                    remote_port_subtype = 7
                if self.rx_mac.match(remote_chassis_id):
                    remote_chassis_id = remote_chassis_id.replace(" ", "-")
                    remote_chassis_id = MACAddressParameter().clean(remote_chassis_id)
                    remote_chassis_id_subtype = 3
                n = {
                    "remote_port": remote_port,
                    "remote_port_subtype": remote_port_subtype,
                    "remote_chassis_id": remote_chassis_id,
                    "remote_chassis_id_subtype": remote_chassis_id_subtype,
                    "remote_system_name": rn,
                }
                i = {"local_interface": local_port, "neighbors": [n]}
                r += [i]
        return r
