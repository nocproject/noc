# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IBM.NOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "IBM.NOS.get_interfaces"
    interface = IGetInterfaces

    rx_int = re.compile(
        r"^(?P<ifname>\S+)\s+(?P<ifindex>\d+)"
        r"\s+(?P<tag>\w)(?:\s+\w){3}\s+(?P<vlan>\d+)\*?\s+(?P<desc>\S+)\s+(?P<vlans>(?:(?:\d+\s+)+))",
        re.MULTILINE,
    )

    rx_desc = re.compile(r"Description\s(?P<desc>.*)")

    rx_vlans = re.compile(r"VLANs\:(?P<vlans>.*)")

    rx_a_stat = re.compile(r"configuration\:\s(?P<admin_status>\w+)")

    rx_o_stat = re.compile(r"^(?P<port>\S+)\s+\d+")

    def get_interfaces_up(self):
        try:
            v = self.cli("show interface status state up")
        except self.CLISyntaxError:
            return []
        r = []
        for match in self.rx_o_stat.finditer(v):
            r += [match.group("port")]
        return r

    def execute_cli(self):
        interfaces = []
        oper_up = self.get_interfaces_up()
        try:
            v = self.cli("show interface information")
        except self.CLISyntaxError:
            return []
        if v:
            for match in self.rx_int.finditer(v):
                ifindex = int(match.group("ifindex")) + 128
                ifname = match.group("ifname")
                iftype = "physical"
                vlan = int(match.group("vlan"))
                vlans = []
                tag = match.group("tag")
                if ifname == "MGT1":
                    desc = match.group("desc")
                else:
                    try:
                        p = self.cli("show interface port %s" % ifname)
                    except self.CLISyntaxError:
                        pass
                    if p:
                        match1 = self.rx_desc.search(p)
                        match2 = self.rx_vlans.search(p)
                        match3 = self.rx_a_stat.search(p)
                        desc = match1.group("desc")
                        if tag == "y":
                            vlans2 = match2.group("vlans")
                            if vlans2 != "":
                                vlans2 = vlans2.strip()
                                vlans3 = vlans2.split(" ")
                                vlans = [int(x) for x in vlans3]
                        a_stat = match3.group("admin_status").lower() == "enabled"
                sub = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": ifname in oper_up,
                    "description": desc,
                    "untagged_vlan": vlan,
                    "tagged_vlans": vlans,
                    "enabled_afi": ["BRIDGE"],
                    "enabled_protocols": [],
                    "snmp_ifindex": ifindex,
                }
                iface = {
                    "name": ifname,
                    "admin_status": a_stat,
                    "oper_status": ifname in oper_up,
                    "description": desc,
                    "type": iftype,
                    "enabled_protocols": [],
                    "snmp_ifindex": ifindex,
                    "subinterfaces": [sub],
                }
                interfaces += [iface]
        return [{"interfaces": interfaces}]
