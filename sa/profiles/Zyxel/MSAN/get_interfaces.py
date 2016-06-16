# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.MSAN.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(BaseScript):
    name = "Zyxel.MSAN.get_interfaces"
    interface = IGetInterfaces

    rx_enet = re.compile(
        r"^\s*(?P<ifname>enet\d+)\s+(?P<descr>.*)\s+(?P<admin_status>V|\-)\s+"
        r"(?:sub|up)\s+.+$", re.MULTILINE)
    rx_enet_o = re.compile(
        r"^\s*switch port enet\d+:\n\s*link status: (?P<oper_status>\S+|down)",
        re.MULTILINE)
    rx_ipif = re.compile(
        r"^\s*(?P<ifname>\S+)\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
        r"(?P<mask>\d+\.\d+\.\d+\.\d+)\s+(?P<vid>\d+|\-)\s*$", re.MULTILINE)
    rx_vlan = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<ports>\S+)/(?P<mode>\S+)\s+\S+\s*"
        r"(?P<name>.*)$", re.MULTILINE)

    def execute(self):
        interfaces = []
        vlans = []
        for match in self.rx_vlan.finditer(self.cli("vlan show")):
            vlans += [{
                "vid": int(match.group("vlan_id")),
                "ports": match.group("ports"),
                "mode": match.group("mode")
            }]
        c = self.cli("switch port show")
        for match in self.rx_enet.finditer(c):
            untagged = 0
            tagged = []
            admin_status = match.group("admin_status") == "V"
            ifname = match.group("ifname")
            if ifname.startswith("enet"):
                v = self.cli("show enet %s" % ifname)
                match1 = self.rx_enet_o.search(v)
                if match1:
                    oper_status = match1.group("oper_status") != "down"
                else:
                    raise self.NotSupportedError()
                    oper_status = admin_status
                port_num = int(ifname[4:].strip()) - 1
                for v in vlans:
                    if v["ports"][port_num] == "F" \
                    and v["mode"][port_num] == "U":
                            untagged = v["vid"]
                    if v["ports"][port_num] == "F" \
                    and v["mode"][port_num] == "T":
                        tagged += [v["vid"]]
            else:
                oper_status = admin_status
            iface = {
                "name": ifname,
                "type": "physical",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [{
                    "name": ifname,
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "enabled_afi": ["BRIDGE"]
                }]
            }
            if untagged:
                iface["subinterfaces"][0]["untagged_vlan"] = untagged
            if tagged:
                iface["subinterfaces"][0]["tagged_vlans"] = tagged
            interfaces += [iface]
        c = self.cli("ip show")
        for match in self.rx_ipif.finditer(c):
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            iface = {
                "name": match.group("ifname"),
                "type": "SVI",
                "admin_status": True,  # always True, since inactive
                "oper_status": True,   # SVIs aren't shown at all
                "subinterfaces": [{
                    "name": match.group("ifname"),
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [ip_address],
                }]
            }
            if match.group("vid") != "-":
                iface["subinterfaces"][0]["vlan_ids"] = [int(match.group('vid'))]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
