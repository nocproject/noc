# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.SANOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Cisco.SANOS.get_interfaces"
    interface = IGetInterfaces

    rx_sh_int = re.compile(
        r"^(?P<interface>.+?) is (?P<oper_status>up|down)( \((?P<reason>.+?)\))?\n"
        r"^\s+Hardware is (?P<hardw>Fibre Channel|GigabitEthernet|FastEthernet)"
        r"(?:,.+?)?\s*(address is (?P<mac>\S{4}\.\S{4}\.\S{4})?.*\n)?"
        r"(?:^\s+Internet address is (?P<ip>\S+)\n)?"
        r"(?:^\s+MTU is (?P<mtu>\d+))?"
        r"(?:.+?\n)?"
        r"(?:^\s+Admin port mode is (?P<portmode>\S+))?",
        re.MULTILINE | re.IGNORECASE)

    def execute(self):
        interfaces = []
        v = self.cli("show interface")
        for match in self.rx_sh_int.finditer(v):
            #hw = match.group("hardw")
            full_ifname = match.group("interface")
            ifname = self.profile.convert_interface_name(full_ifname)
            if ifname[:4] == "mgmt":
                iftype = "management"
            if ifname[:5] == "iscsi":
                iftype = "other"
            elif ifname[:3] == "sup":
                iftype = "other"
            else:
                iftype = "physical"
            o_stat = match.group("oper_status").lower() == "up"
            if match.group("reason"):
                reason = match.group("reason")
                if reason == "SFP not present":
                    a_stat = True
                elif reason == "Link failure or not-connected":
                    a_stat = True
                elif reason == "Administratively down":
                    a_stat = False
            else:
                a_stat = o_stat
            iface = {
                "name": ifname,
                "type": iftype,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_protocols": [],
                "subinterfaces": []
            }
            sub = {
                "name": ifname,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "enabled_afi": []
            }
            if match.group("mac"):
                iface["mac"] = match.group("mac")
                sub["mac"] = match.group("mac")
            if match.group("ip"):
                sub["enabled_afi"] += ["IPv4"]
                sub["ipv4_addresses"] = [match.group("ip")]
            if match.group("portmode") and match.group("portmode") == "ISCSI":
                sub["enabled_afi"] += ["iSCSI"]
            if match.group("mtu"):
                sub["mtu"] = int(match.group("mtu"))
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
