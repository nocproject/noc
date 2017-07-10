# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_lldp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4


class Script(BaseScript):
    name = "Cisco.IOS.get_lacp_neighbors"
    interface = IGetLACPNeighbors
    split_group_re = re.compile(r"\nChannel group\s+(\d+)")
    split_group2_re = re.compile(r"\nChannel group\s+(\d+)\s+neighbors")
    split_port_re = re.compile(r"Port:")
    split_info_re = re.compile(r"----.+Channel group\s*=\s*(?P<chan_group>\d+)\s.+"
                               r"Port-channel\s*=\s*(?P<port_chan>\S+)\s.+"
                               r"Local information:(?P<local_info>.+)"
                               r"Partner's information:(?P<part_info>.+)\n", re.IGNORECASE | re.DOTALL)

    def execute(self):
        r = []
        v = self.cli("show lacp sys-id")
        sys_id = v.split(",")[1].strip()
        try:
            v = self.cli("show lacp internal")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        first_line = True
        port = {}
        for block in self.split_group_re.split(v):
            table = False
            for l in block.splitlines():
                if not l:
                    continue
                l_l = l.split()
                if table:
                    port[l_l[0]] = int(l_l[6][2:], 16)
                if l_l[0] == "Port":
                    table = True

        try:
            v = self.cli("show lacp neighbor detail")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        is_block = False
        for block in self.split_group2_re.split(v)[1:]:
            if not is_block:
                chan_num = block
                is_block = True
                continue
            bundle = []
            for l in block.splitlines():
                if not l:
                    continue
                l_l = l.split()
                if l_l[0] in port:
                    bundle += [{
                        "interface": l_l[0],
                        "local_port_id": port[l_l[0]],
                        "remote_system_id": l_l[1].split(",")[1],
                        "remote_port_id": int(l_l[2], 16)
                    }]

            pass
            """
            for port in self.split_port_re.split(block):
                port_info = self.split_info_re.match(port)
                if not port_info:
                    continue
                local_info = port_info.group("local_info")
                local_info = local_info.splitlines()[-1]
                part_info = port_info.group("part_info")
                part_info = part_info.splitlines()[-1]
                group_interface = port_info.group("port_chan")
                bundle += [{
                    "interface": local_info[0],
                    "local_port_id": local_info[6],
                    "remote_system_id": "",
                    "remote_port_id": part_info[6]
                }]
            """
            r += [{
                "lag_id": chan_num,
                "interface": "Port-Channel" + chan_num,
                "system_id": sys_id,
                "bundle": bundle
            }]
            is_block = False
        "show lacp internal detail"
        "Local information:"
        "Partner's information:"
        return r
