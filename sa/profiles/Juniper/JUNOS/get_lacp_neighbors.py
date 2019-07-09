# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_lacp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors


class Script(BaseScript):
    name = "Juniper.JUNOS.get_lacp_neighbors"
    interface = IGetLACPNeighbors

    rx_ifname = re.compile(r"^Aggregated interface: (ae\d+)\s*\n", re.MULTILINE)
    rx_neighbor = re.compile(
        r"^\s+(?P<ifname>\S{2}\-\S+\d+)\s+(?P<role>Actor|Partner)\s+"
        r"(?P<sys_prio>\d+)\s+(?P<sys_id>\S+)\s+(?P<port_prio>\d+)\s+"
        r"(?P<port_num>\d+)\s+(?P<port_key>\d+)\s*\n",
        re.MULTILINE,
    )

    def execute(self):
        try:
            v = self.cli("show lacp interfaces")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        ifaces = self.rx_ifname.findall(v)
        for i in ifaces:
            v = self.cli('show interfaces %s extensive | find "LACP info"' % i)
            if "Pattern not found" in v:
                continue
            bundle = []
            for match in self.rx_neighbor.finditer(v):
                if match.group("role") == "Actor":
                    sys_id = match.group("sys_id")
                    ifname, unit = match.group("ifname").split(".")
                    bundle += [{"interface": ifname, "local_port_id": match.group("port_num")}]
                else:
                    bundle[-1].update(
                        {
                            "remote_system_id": match.group("sys_id"),
                            "remote_port_id": match.group("port_num"),
                        }
                    )
            r += [{"lag_id": i[2:], "interface": i, "system_id": sys_id, "bundle": bundle}]
        return r
