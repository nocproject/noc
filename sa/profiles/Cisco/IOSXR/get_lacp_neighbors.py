# ---------------------------------------------------------------------
# Cisco.IOSXR.get_lacp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors


class Script(BaseScript):
    name = "Cisco.IOSXR.get_lacp_neighbors"
    interface = IGetLACPNeighbors
    pattern_split_1 = r"^(\s+[-]+)+$"
    pattern_split_2 = r"^\s+Link is.+"
    pattern_split_3 = r"[=]+"
    split_group_re = re.compile(r"\nBundle-\w+(\d+)")
    split_group2_re = re.compile(r"\nBundle-\D+(\d+)")
    split_group3_re = re.compile(r"\n?[=]+")

    rx_sys_id = re.compile(
        r"\s*(?P<sys_id>\w{2}-\w{2}-\w{2}-\w{2}-\w{2}-\w{2})",
        re.IGNORECASE | re.DOTALL,
    )

    def execute(self):
        r = []
        v = self.cli("show lacp system-id")
        sys_id = self.rx_sys_id.search(v)
        sys_id = sys_id.group("sys_id")

        try:
            v = self.cli("show bundle")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        port = {}
        for block in self.split_group_re.split(v):
            table = False
            for l in block.splitlines():
                if not l:
                    continue
                elif re.match(self.pattern_split_1, l) or re.match(self.pattern_split_2, l):
                    continue
                l_l = l.split()
                if table:
                    port[int(l_l[4][2:], 16)] = l_l[0]
                if l_l[0] == "Port":
                    table = True

        try:
            v = self.cli("show lacp io")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for cn_block, block in enumerate(self.split_group2_re.split(v)[1:], start=1):
            if cn_block % 2:
                chan_num = block
                continue

            block = block.strip()
            bundle = []
            for sub_block in self.split_group3_re.split(block)[1:]:
                dc_bundle = dict()
                sub_block = sub_block.strip()
                if not sub_block:
                    continue

                for l in sub_block.splitlines():
                    if re.match(r"Partner system:.+", l):
                        l_l = l.split()
                        dc_bundle["remote_system_id"] = l_l[3]
                    elif re.match(r"Partner port:.+", l):
                        l_l = l.split()
                        dc_bundle["remote_port_id"] = int(l_l[3], 16)
                    elif re.match(r"Actor port:.+", l):
                        l_l = l.split()
                        actor_port = int(l_l[3], 16)

                if actor_port in port:
                    dc_bundle["interface"] = port[actor_port]
                    dc_bundle["local_port_id"] = actor_port
                    bundle += [dc_bundle]

            if bundle:
                r += [
                    {
                        "lag_id": chan_num,
                        "interface": "Bundle-Ether" + chan_num,
                        "system_id": sys_id,
                        "bundle": bundle,
                    }
                ]
        return r
