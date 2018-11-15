# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import six
from collections import defaultdict
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.MES.get_portchannel"
    interface = IGetPortchannel
    cache = True

    rx_lag = re.compile(
        r"^(?P<port>Po\d+)\s+(?P<type1>\S+):\s+(?P<interfaces1>\S+)+(\s+(?P<type2>\S+):\s+(?P<interfaces2>\S+)$|$)",
        re.MULTILINE
    )

    rx_lacp = re.compile(r"^\s+Attached Lag id:$", re.MULTILINE)

    def execute_snmp(self):
        r = defaultdict(list)
        names = {x: y for y, x in six.iteritems(self.scripts.get_ifindexes())}
        for ifindex, sel_pc, att_pc in self.snmp.get_tables(
                [mib["IEEE8023-LAG-MIB::dot3adAggPortSelectedAggID"],
                 mib["IEEE8023-LAG-MIB::dot3adAggPortAttachedAggID"]]):
            if att_pc:
                r[names[int(att_pc)]] += [names[int(ifindex)]]
        return [{"interface": pc,
                 "type": "L",
                 "members": r[pc]} for pc in r if pc.startswith("Po")]

    def execute_cli(self):
        res = []
        # Fallback to CLI
        if (self.match_version(version__regex="[12]\.[15]\.4[4-9]") or
                self.match_version(version__regex="4\.0\.[4-7]$")):
            cmd = self.cli("show interfaces channel-group", cached=True)
        else:
            cmd = self.cli("show interfaces port-channel", cached=True)
        for match in self.rx_lag.finditer(cmd):
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
            lacp = self.cli("show lacp Port-Channel")
            match_ = self.rx_lacp.search(lacp)
            if match_:
                l_type = "L"
            else:
                l_type = "S"
            res += [
                {
                    "interface": match.group("port").lower(),
                    # "interface": match.group("port"),
                    "type": l_type,
                    "members": memb,
                }
            ]
        return res
