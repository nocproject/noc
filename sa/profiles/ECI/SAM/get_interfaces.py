# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ECI.SAM.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# -------------------------------------------------------------------

# python module
from __future__ import print_function
import re
# NOC module
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "ECI.SAM.get_interfaces"
    interface = IGetInterfaces
    reuse_cli_session = False
    keep_cli_session = False

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
        r"^(?P<ifname>\S+)\s+\(unit number (?P<unit>\S+)\):\s*\n"
        r"^.+?\n"
        r"^.+?\n"
        r"(^\s+Internet address: (?P<ip>\S+)\s*\n)?"
        r"(^\s+Broadcast address: \S+\s*\n)?"
        r"(^\s+Netmask (?P<nmask>\S+) Subnetmask (?P<smask>\S+)\s*\n)?"
        r"(^\s+Ethernet address is (?P<mac>\S+)\s*\n)?"
        r"(^\s+Metric is \d+\s*\n)?"
        r"(^\s+Maximum Transfer Unit size is (?P<mtu>\d+)\s*\n)?",
        re.MULTILINE)

    def execute(self):
        self.cli("IFSHOW ?")
        cmd = self.cli("IFSHOW")
        interfaces = []
        mac = None
        c = cmd.split("\n\n")
        if self.match_version(version__contains="IPNI"):
            for i in c:
                i = i.strip()
                if not i:
                    continue
                match = self.rx_sh_int.search(i)
                if match:
                    mac = match.group("mac")
                else:
                    match = self.rx_sh_int2.search(i)
                    if not match:
                        continue
                ifname = match.group("ifname")
                typ = self.profile.get_interface_type(ifname)
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
                    "type": typ,
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
        if not interfaces:
            for match in self.rx_sh_int3.finditer(cmd):
                mac = match.group("mac")
                mtu = match.group("mtu")
                name = match.group("ifname")
                unit = match.group("unit")
                ifname = "%s%s" % (name, unit)
                typ = self.profile.get_interface_type(name)
                iface = {
                    "name": ifname,
                    "type": typ,
                    "subinterfaces": [{
                        "name": ifname,
                    }]
                }
                ip = match.group("ip")
                if ip:
                    try:
                        n = match.group("nmask")
                        nn = [int(n[2:][ii:ii + 2], 16) for ii in range(0, len(n[2:]), 2)]
                    except Exception:
                        print("%s %s %s\n" % (iface, n, mac))
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
                    iface["subinterfaces"][0][ip_interfaces] = ip_list
                    iface["subinterfaces"][0]["enabled_afi"] = enabled_afi
                if mac:
                    iface["mac"] = mac
                    iface["subinterfaces"][0]["mac"] = mac
                if mtu:
                    iface["subinterfaces"][0]["mtu"] = mtu
                interfaces += [iface]
        return [{"interfaces": interfaces}]
