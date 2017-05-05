# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.7302.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.text import *
from noc.core.ip import IPv4
from collections import defaultdict


class Script(BaseScript):
    name = "Alcatel.7302.get_interfaces"
    interface = IGetInterfaces

    rx_ifname = re.compile("port : (?P<ifname>\S+)")
    rx_ifindex = re.compile("if-index : (?P<ifindex>\d+)")
    rx_ififo = re.compile("info : \"(?P<info>.+?)\"")
    rx_type = re.compile("type : (?P<type>\S+)")
    rx_mac = re.compile("phy-addr : (?P<mac>\S+)")
    rx_admin_status = re.compile("admin-status : (?P<admin_status>up|down|not-appl)")
    rx_oper_status = re.compile("opr-status : (?P<oper_status>up|down)")
    rx_mtu = re.compile("largest-pkt-size : (?P<mtu>\d+)")
    rx_vpi_vci = re.compile("\d+:(?P<vpi>\d+):(?P<vci>\d+)")

    types = {
        "ethernet": "physical",
        "slip": "tunnel",
        "xdsl-line": "physical",
        "xdsl-channel": "physical",
        "atm-bonding": "physical",
        "atm": "physical",
        "sw-loopback": "loopback"
    }

    def execute(self):
        interfaces = []
        self.cli("environment inhibit-alarms mode batch terminal-timeout timeout:120")
        v = self.cli("show interface port detail")
        for p in v.split("----\nport\n----"):
            match = self.rx_ifname.search(p)
            if not match:
                continue
            ifname = match.group("ifname")
            match = self.rx_vpi_vci.search(ifname)
            if not match:
                match = self.rx_admin_status.search(p)
                admin_status = match.group("admin_status") == "up"
                match = self.rx_oper_status.search(p)
                oper_status = match.group("oper_status") == "up"
                match = self.rx_type.search(p)
                iftype = self.types[match.group("type")]
                match = self.rx_ifindex.search(p)
                ifindex = match.group("ifindex")
                i = {
                    "name": ifname,
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "type": iftype,
                    "snmp_ifindex": int(ifindex),
                    "enabled_protocols": [],
                    "subinterfaces": [{
                        "name": ifname,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": []
                    }],
                }
                match = self.rx_mac.search(p)
                if match:
                    i["mac"] = match.group("mac")
                    i["subinterfaces"][0]["mac"] = match.group("mac")
                match = self.rx_mtu.search(p)
                if match:
                    i["subinterfaces"][0]["mtu"] = match.group("mtu")
                if iftype != "tunnel":
                    i["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
                interfaces += [i]
            else:
                continue
        return [{"interfaces": interfaces}]
