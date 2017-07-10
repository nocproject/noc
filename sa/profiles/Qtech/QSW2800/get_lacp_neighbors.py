# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2800.get_lacp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import itertools
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4


class Script(BaseScript):
    name = "Qtech.QSW2800.get_lacp_neighbors"
    interface = IGetLACPNeighbors
    split_re = re.compile(r"Port-group\snumber:\s*(?P<p_id>\d+).+", re.IGNORECASE)
    split2_re = re.compile(r"\s*Port-group\snumber:\s*(?P<p_id>\d+),"
                          r"\s*Mode:\s*(?P<mode>\S+),"
                          r"\s*Load-balance:\s*(?P<load_bal>\S+)\s*", re.IGNORECASE)

    port_id = re.compile(r"\s*(?P<port_name>\S+).+index\sis\s(\d+)(\s*|\n)", re.IGNORECASE)

    def execute(self):
        r = []
        try:
            v = self.cli("show port-group detail")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        first = True
        pc_name = ""
        # for block in itertools.islice(self.split_re.split(v), 1, None, 4):
        for block in self.split_re.split(v)[1:]:
            # print("Split %s\n\n" % self.split_re.split(v))
            if not block:
                continue
            if first:
                first = False
                pc_name = block
                continue
            # pc_name = block
            self.logger.debug("Block is: %s\n\n" % block)
            out = self.profile.parse_table(block.lstrip(), part_name="lacp")
            self.logger.debug("Out, %s\n\n" % out)
            bundle = []
            if not out.get("Remote", None):
                first = True
                continue
            for bun in out["Local"]["table"]:
                # PortID LACP = ifindex
                index = self.port_id.findall(self.cli("show interface %s | i index" % bun[0]))
                # Find in partner table by interface
                partner = [(i[4].split(",")[1], i[1]) for i in out["Remote"]["table"] if bun[0] in i]
                if partner:
                    r_id, r_p_id = partner[0]
                else:
                    self.logger.info("Partner for interface %s not find, skip" % bun[0])
                    # Partner not find, skip
                    continue

                bundle += [{
                    "interface": bun[0],
                    "local_port_id": int(index[0][1]),
                    "remote_system_id": r_id,
                    "remote_port_id": int(r_p_id)
                }]

            r += [{"lag_id": int(pc_name),
                   "interface": "Port-Channel" + pc_name,
                   "system_id": out["lacp"]["System ID"].split(",")[1],
                   "bundle": bundle
                   }]
            first = True

        return r
