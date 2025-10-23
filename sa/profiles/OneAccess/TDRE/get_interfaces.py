# ---------------------------------------------------------------------
# OneAccess.TDRE.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "OneAccess.TDRE.get_interfaces"
    interface = IGetInterfaces

    rx_hw_port = re.compile(r"(?P<port>hwPort\[\d\])")
    rx_eth_iface = re.compile(
        r"^\s+ifDescr = (?P<ifname>.+)\s*\n"
        r"^\s+ifType = ethernet-csmacd\s*\n"
        r"^\s+ifMtu = (?P<mtu>\d+)\s*\n"
        r"^\s+ifOperStatus = (?P<oper_status>\S+)\s*\n"
        r"^\s+ifLastChange = .+\n"
        r"^\s+ifSpeed = \d+\s*\n"
        r"(^.+\n)?"
        r"^\s+snmpIndex = (?P<snmp_ifindex>\d+)\s*\n",
        re.MULTILINE | re.DOTALL,
    )
    rx_vlan = re.compile(
        r"^\s+vid = (?P<vlan_id>\d+)\s*\n(?P<ports>.+?)\n^\s+localPort",
        re.MULTILINE | re.DOTALL,
    )
    rx_vlan_port = re.compile(r"hwPort(?P<port>\d) = (?P<type>\S+)")
    rx_mac = re.compile(r"macAddress = (?P<mac>\S+)")
    rx_ip_iface = re.compile(
        r"^\s+ifDescr = (?P<descr>.+)\n"
        r"^\s+ifType = (?P<iftype>\S+)\s*\n"
        r"^\s+ifOperStatus = (?P<oper_status>\S+)\s*\n"
        r"^\s+ifLastChange = .+\n"
        r"^\s+address = (?P<ip_address>\S+)\s*\n"
        r"^\s+mask = (?P<ip_mask>\S+)\s*\n"
        r"^\s+secondaryIp =\s*"
        r"^\s+{\s*"
        r"(^\s+.+\n)?"
        r"^\s+}\s*",
        re.MULTILINE,
    )

    IF_TYPES = {"softwareLoopback": "loopback", "ethernet-csmacd": "SVI"}

    def execute(self):
        interfaces = []
        self.cli("SELGRP Status")
        for etherswitch in ["1", "2"]:
            c = self.cli("GET ethernet%s/" % etherswitch)
            match = self.rx_eth_iface.search(c)
            ifname = match.group("ifname").replace('"', "")
            # ifname = "port" + ifname[-1]
            iface = {
                "name": ifname,
                "oper_status": match.group("oper_status") == "up",
                "type": "physical",
                # "description": match.group("ifname").replace("\"", ""),
                "snmp_ifindex": match.group("snmp_ifindex"),
                "subinterfaces": [
                    {
                        "name": ifname,
                        "oper_status": match.group("oper_status") == "up",
                        "enabled_afi": ["BRIDGE"],
                        "mtu": match.group("mtu"),
                        "tagged_vlans": [],
                    }
                ],
            }
            interfaces += [iface]
            c = self.cli("GET ethernet%s/" % etherswitch, command_submit=b"\x09")
            self.cli("")
            for i in self.rx_hw_port.finditer(c):
                v = self.cli("GET ethernet%s/%s/" % (etherswitch, i.group("port")))
                match = self.rx_eth_iface.search(v)
                ifname = match.group("ifname").replace('"', "")
                ifname = "port" + ifname[-1]
                iface = {
                    "name": ifname,
                    "oper_status": match.group("oper_status") == "up",
                    "type": "physical",
                    "description": match.group("ifname").replace('"', ""),
                    "snmp_ifindex": match.group("snmp_ifindex"),
                    "subinterfaces": [
                        {
                            "name": ifname,
                            "oper_status": match.group("oper_status") == "up",
                            "enabled_afi": ["BRIDGE"],
                            "mtu": match.group("mtu"),
                            "tagged_vlans": [],
                        }
                    ],
                }
                interfaces += [iface]
            c = self.cli("GET ethernet%s/vtuTable[]/" % etherswitch)
            for match in self.rx_vlan.finditer(c):
                vlan_id = match.group("vlan_id")
                for match1 in self.rx_vlan_port.finditer(match.group("ports")):
                    vtype = match1.group("type")
                    if vtype == "--":
                        continue
                    port = "port" + match1.group("port")
                    for i in interfaces:
                        if port == i["name"]:
                            if vtype == "untag":
                                i["subinterfaces"][0]["untagged_vlan"] = vlan_id
                            else:
                                i["subinterfaces"][0]["tagged_vlans"] += [vlan_id]
                            break
        c = self.cli("GET ip/router/interfaces[]/")
        for match in self.rx_ip_iface.finditer(c):
            ip = match.group("ip_address")
            mask = IPv4.netmask_to_len(match.group("ip_mask"))
            ifname = match.group("descr").replace('"', "")
            sub = {
                "name": ifname,
                # "admin_status": True,
                "oper_status": match.group("oper_status") == "up",
                "enabled_afi": ["IPv4"],
                "ipv4_addresses": ["%s/%s" % (ip, mask)],
            }
            found = False
            if ifname.startswith("eth"):
                ifname1 = ifname[:4]
                for i in interfaces:
                    if i["name"] == ifname1:
                        sub["enabled_afi"] = ["BRIDGE", "IPv4"]
                        i["subinterfaces"][0].update(sub)
                        found = True
                        break
            if found:
                continue
            iface = {
                "name": ifname,
                # "admin_status": True,
                "oper_status": match.group("oper_status") == "up",
                "type": self.IF_TYPES[match.group("iftype")],
                "subinterfaces": [sub],
            }
            interfaces += [iface]
        c = self.cli("GET bridge/bridgeGroup/macAddress")
        match = self.rx_mac.search(c)
        mac = match.group("mac")
        for i in interfaces:
            if i["name"] == "bridge":
                i["mac"] = mac
                i["subinterfaces"][0]["mac"] = mac
                break
        return [{"interfaces": interfaces}]
