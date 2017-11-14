# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES.get_lacp_neighbors
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetlacpneighbors import IGetLACPNeighbors


class Script(BaseScript):
    name = "Eltex.MES.get_lacp_neighbors"
    interface = IGetLACPNeighbors
    rx_pc = re.compile(
        r"Port-Channel\s(?P<ifname>\S+)"
        r"\s+Port Type (?P<portype>Unknown|Gigabit Ethernet)"
        r"\s+Attached Lag id:"
        r"\s+Actor"
        r"\s+System Priority:(?P<sp>\S+)"
        r"\s+MAC Address:\s+(?P<mac>\S+)"
        r"\s+Admin Key:\s+(?P<ak>\S+)"
        r"\s+Oper Key:\s+(?P<ok>\S+)"
        r"\s+Partner"
        r"\s+System Priority:(?P<psp>\S+)"
        r"\s+MAC Address:\s+(?P<pmac>\S+)"
        r"\s+Oper Key:\s+(?P<pok>\S+)",
        re.MULTILINE
    )
    rx_lag = re.compile(
        r"^(?P<port>\S+\d+)\s+(?P<type1>\S+):\s+(?P<interfaces1>\S+)+"
        r"(\s+(?P<type2>\S+):\s+(?P<interfaces2>\S+)$|$)",
        re.MULTILINE
    )
    rx_iface = re.compile(
        r"(?P<ifname>\S+\d+) LACP parameters:"
        r"\s+Actor"
        r"\s+system priority:\s+(?P<sp>\S+)"
        r"\s+system mac addr:\s+(?P<mac>\S+)"
        r"\s+port Admin key:\s+(?P<ak>\S+)"
        r"\s+port Oper key:\s+(?P<ok>\S+)"
        r"\s+port Oper number:\s+(?P<lportid>\S+)"
        r"[\s\S]+?"
        r"\s+system mac addr:\s+(?P<rmac>\S+)"
        r"[\s\S]+?"
        r"\s+port Oper number:\s+(?P<rportid>\S+)",
        re.MULTILINE
    )

    def execute(self):
        r = []
        d = {}
        bundle = []
        if (
            self.match_version(version__regex="[12]\.[15]\.4[4-9]") or
            self.match_version(version__regex="4\.0\.[4-7]$")
        ):
            cmd = self.cli("show interfaces channel-group")
        else:
            cmd = self.cli("show interfaces port-channel")
        for match in self.rx_lag.finditer(cmd):
            ifname = match.group("port")
            members = match.group("interfaces1").split(',')
            memb = []
            for iface in members:
                if '-' in iface:
                    mas = iface.split('/')
                    R = mas[2].split('-')
                    for i in range(int(R[0]), int(R[1]) + 1):
                        memb += [mas[0] + '/' + mas[1] + '/' + str(i)]
                else:
                    memb += [iface]
            members2 = match.group("interfaces2")
            if members2:
                members2 = members2.split(',')
                for iface in members2:
                    if '-' in iface:
                        mas = iface.split('/')
                        R = mas[2].split('-')
                        for i in range(int(R[0]), int(R[1]) + 1):
                            memb += [mas[0] + '/' + mas[1] + '/' + str(i)]
                    else:
                        memb += [iface]
            d[ifname] = memb
        for pc in d.items():
            sys_id = ""
            # Get lacp port-channel
            chan_num = str(pc[0]).replace("Po", "")
            v = self.cli("show lacp %s" % pc[0])
            for p in self.rx_pc.finditer(v):
                if int(p.group("pok")) == 1:
                    sys_id = p.group("mac")
            # Get bundle
            for i in pc[1]:
                sl = self.cli("show lacp %s" % i)
                for match in self.rx_iface.finditer(sl):
                    if match:
                        sys_id = match.group("mac")
                        rsys_id = match.group("rmac")
                        lportid = match.group("lportid")
                        rportid = match.group("rportid")
                        bundle += [{
                            "interface": i,
                            "local_port_id": lportid,
                            "remote_system_id": rsys_id,
                            "remote_port_id": int(rportid)
                        }]
            if sys_id:
                r += [{
                    "lag_id": chan_num,
                    "interface": "Port-Channel" + pc[0],
                    "system_id": sys_id,
                    "bundle": bundle
                }]
        return r
