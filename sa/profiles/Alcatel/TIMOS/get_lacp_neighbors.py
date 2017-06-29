# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.TIMOS.get_lacp_neighbors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors
from noc.sa.interfaces.base import MACAddressParameter
from noc.lib.validators import is_int, is_ipv4


class Script(BaseScript):
    name = "Alcatel.TIMOS.get_lacp_neighbors"
    interface = IGetLACPNeighbors
    split_re = re.compile(r"(\S+)'s state information is:", re.IGNORECASE)
    sys_id = re.compile(r"System\sId\s*:\s*(?P<system_id>\S+)\s")

    def execute(self):
        r = []
        for lag in self.scripts.get_portchannel():
            try:
                v = self.cli("show %s lacp-partner" % lag["interface"].replace("-", " "))
            except self.CLISyntaxError:
                raise self.NotSupportedError()

            try:
                v_s = self.sys_id.findall(self.cli("show lag detail"))[0]
            except self.CLISyntaxError:
                raise self.NotSupportedError()

            m = {}
            is_table = False
            is_table_body = False
            bundle = []
            for l in v.splitlines():
                if ":" in l:
                    m[l.split(":", 1)[0].strip()] = l.split(":", 1)[1]
                if "Ports Partner operational information" in l:
                    is_table = True
                    continue
                if is_table and "------------" in l:
                    is_table_body = True
                    continue
                if is_table_body and "========" in l:
                    is_table = False
                    is_table_body = False
                if is_table_body:
                    row = l.split()
                    bundle += [{
                        "interface": row[0],
                        "local_port_id": row[1],
                        "remote_system_id": m["Partner system ID"].strip(),
                        "remote_port_id": row[2]
                    }]
            r += [{"lag_id": lag["interface"].split("-")[1],
                   "interface": lag["interface"],
                   "system_id": v_s,
                   "bundle": bundle
                   }]
        return r
