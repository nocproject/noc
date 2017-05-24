# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DCN.DCWS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "DCN.DCWS.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_sh_int = re.compile(
        r"\s+(?P<interface>\S+)\s+is\s+(?P<admin_status>up|down),\s+line\s+protocol\s+is\s+(?P<oper_status>up|down)"
        r"\s+(?P<ifname>[^\n]+)"
        r"\s+Hardware is (?P<hardw>[^\n]+)",
    re.MULTILINE | re.IGNORECASE)
    rx_mac = re.compile(
        r"\s+address\s+is\s+(?P<mac>\S+)",
    re.MULTILINE | re.IGNORECASE)
    rx_alias = re.compile(
        r"\s+alias\s+name is (?P<alias>\S+)\s",
    re.MULTILINE | re.IGNORECASE)
    rx_index = re.compile(
        r"\s*index is (?P<ifindex>\S+)",
    re.MULTILINE | re.IGNORECASE)

    def execute(self):
        interfaces = []
        v = self.cli("show interface", cached=True)
        for match in self.rx_sh_int.finditer(v):
            name = match.group("interface")
            ifname = match.group("ifname")
            hw = match.group("hardw")
            matchmac = self.rx_mac.search(hw)
            if matchmac:
                mac = matchmac.group("mac")
            matchalias = self.rx_alias.search(ifname)
            if matchalias:
                alias = matchalias.group("alias")
            matchindex = self.rx_index.search(ifname)
            if matchindex:
                ifindex = matchindex.group("ifindex")
            a_stat = match.group("admin_status").lower() == "up"
            o_stat = match.group("oper_status").lower() == "up"
            #print name, mac, index, alias, a_stat, o_stat

            interfaces += [{
                "type": "physical",
                "name": name,
                "mac": mac,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "description": alias,
                "snmp_ifindex": ifindex,
                "subinterfaces": [{
                    "name": name,
                    "mac": mac,
                    "admin_status": a_stat,
                    "oper_status": o_stat,
                    "description": alias,
                    "snmp_ifindex": ifindex,
                    "enabled_afi": ["BRIDGE"],
                }]
            }]
        return [{"interfaces": interfaces}]

