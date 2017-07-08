# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ECI.SAM.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.sa.interfaces.base import MACAddressParameter
from noc.core.ip import IPv4
import re


class Script(BaseScript):
    name = "ECI.SAM.get_interfaces"
    interface = IGetInterfaces

    rx_sh_int = re.compile(
        r"^(?P<ifname>\S+)\s+Link type:(?P<type>\S+)\s+HWaddr\s+(?P<mac>\S+)\s+\S+\s+inet\s(?P<ip>\S+)"
        r"\s+mask\s+(?P<mask>\S+)\s+(?:.*\s*)(?:(inet\s(?P<ip2>\S+)\s+mask\s+(?P<mask2>\S+)))?"
        r"\s+[\S ]+\s+MTU:(?P<mtu>\S+)\s+\S+\s+\S+\s+ifindex:(?P<ifindex>\S+)",
        re.MULTILINE)
    rx_sh_int2 = re.compile(
        r"^(?P<ifname>\S+)\s+Link type:(?P<type>\S+\s\S+|\S+)\s+\S+\s+inet\s+(?P<ip>\S+)\s+mask\s+"
        r"(?P<mask>\S+)\s+(?:.*\s*)(?:(inet\s(?P<ip2>\S+)\s+mask\s+(?P<mask2>\S+)))?\s+[\S ]+\s+"
        r"MTU:(?P<mtu>\S+)\s+\S+\s+\S+\s+ifindex:(?P<ifindex>\S+)",
        re.MULTILINE)
    rx_sh_int3 = re.compile(
        r"^(?P<ifname>\S+)\s+\(unit number\s(?P<unit>\S+)\):\s+[\S ]+\s+[\S ]+\s+\S+"
        r"\s\S+:\s(?P<ip>\S+)\s+(?:.*\s*)Netmask\s(?P<nmask>\S+)\sSubnetmask\s(?P<smask>\S+)"
        r"\s+(?:Ethernet\saddress\sis\s(?P<mac>\S+))?",
        re.MULTILINE)
    def execute(self):
        self.cli("IFSHOW ?")
        cmd = self.cli("IFSHOW")
        interfaces = []
        mac = None
        c = cmd.split("\n\n")
        if (self.match_version(version__contains="IPNI")):
            for i in c:
                i = i.strip()
                if not i:
                    continue
                match = self.rx_sh_int.search(i)
                if match:
                    mac = match.group("mac")
                else:
                    match = self.rx_sh_int2.search(i)
                ifname = match.group("ifname")
                mtu = match.group("mtu")
                ifindex = match.group("ifindex")
                ip = match.group("ip")
                netmask = match.group("mask")
                mask = str(IPv4.netmask_to_len(netmask))
                ip = ip + '/' + mask
                ip_list = [ip]
                enabled_afi = []
                if ":" in ip:
                    ip_interfaces = "ipv6_addresses"
                    enabled_afi += ["IPv6"]
                else:
                    ip_interfaces = "ipv4_addresses"
                    enabled_afi += ["IPv4"]
                iface = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [{
                        "name": ifname,
                        "admin_status": True,
                        "oper_status": True,
                        "snmp_ifindex": ifindex,
                        "mtu": mtu,
                        ip_interfaces: ip_list,
                        "enabled_afi": enabled_afi
                    }]
                }
                if mac:
                    iface["mac"] = mac
                    iface["subinterfaces"][0]["mac"] = mac
                interfaces += [iface]
        else:
            print cmd
            for match in self.rx_sh_int3.finditer(cmd):
                mac = match.group("mac")
                ifname = match.group("ifname")
                ip = match.group("ip")
                n = match.group("nmask")
                nn = [int(n[2:][i:i+2],16) for i in range(0,len(n[2:]),2)]
                netmask = "%d.%d.%d.%d" % (nn[0], nn[1], nn[2], nn[3],)
                mask = str(IPv4.netmask_to_len(netmask))
                ip = ip + '/' + mask
                ip_list = [ip]
                enabled_afi = []
                if ":" in ip:
                    ip_interfaces = "ipv6_addresses"
                    enabled_afi += ["IPv6"]
                else:
                    ip_interfaces = "ipv4_addresses"
                    enabled_afi += ["IPv4"]
                iface = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [{
                        "name": ifname,
                        "admin_status": True,
                        "oper_status": True,
                        ip_interfaces: ip_list,
                        "enabled_afi": enabled_afi
                    }]
                }
                if mac:
                    iface["mac"] = mac
                    iface["subinterfaces"][0]["mac"] = mac
                interfaces += [iface]
        return [{"interfaces": interfaces}]
