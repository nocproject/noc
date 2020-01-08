# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ECI.HiFOCuS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# -------------------------------------------------------------------

# Python modules
import re

# Third-party modules
import six

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.mib import mib


class Script(BaseScript):
    name = "ECI.HiFOCuS.get_interfaces"
    interface = IGetInterfaces
    reuse_cli_session = False
    keep_cli_session = False
    always_prefer = "S"

    rx_table_spliter = re.compile(r"(?:\+-*)+\n")

    rx_snmp_iface = re.compile(
        r".+:\s*Shelf-(?P<shelf>\d+)\s*Interface-(?P<slot>\d+)\s*"
        r"Port-(?P<port>\d+)\s*Mani-(?P<mani>\d+)\s*"
        r"Layer-(?P<layer>\d+)\s*Loc-(?P<loc>\d+)\s*Uni-(?P<uni>\d+)\s*"
    )

    rx_iface_name = re.compile(r"(?P<ifname>\S+)(\s*.\(.+(?P<unit_num>\d+)\):|)")
    rx_iface_mac = re.compile(r"(?:Ethernet address is|HWaddr)\s+(?P<mac>\S+)")
    rx_iface_mtu = re.compile(r"(Maximum Transfer Unit size is|MTU:)\s*(?P<mtu>\d+)")
    rx_iface_ifindex = re.compile(r"ifindex:(?P<ifindex>\d+)")
    rx_iface_l3_address1 = re.compile(
        r"\s+inet\s+(?P<address>\S+)\s+"
        r"mask\s+(?P<netmask>\S+)\s*"
        r"(broadcast\s+(?P<broadcast>\S+))?",
        re.MULTILINE,
    )
    rx_iface_l3_address2 = re.compile(
        r"\s+Internet address:\s+(?P<address>\S+)\n"
        r"(?:\s+Broadcast address:\s+(?P<broadcast>\S+)\n)?"
        r"\s+Netmask\s+(?P<netmask>\S+)\s*Subnetmask\s+(?P<subnetmask>\S+)",
        re.MULTILINE,
    )
    rx_l3_iface_splitter = rx_splitter = re.compile(r"^(?P<ifname>\S+\s+\(.+\):|\S+)", re.MULTILINE)

    def get_l3_interfaces(self):
        v = self.cli("IFSHOW")
        interfaces = {}
        ifname = None
        for block in self.rx_l3_iface_splitter.split(v)[1:]:
            if not block:
                continue
            match = self.rx_iface_name.match(block)
            if match:
                ifname = match.group("ifname")
                if match.group("unit_num"):
                    ifname += match.group("unit_num")
                iftype = self.profile.get_interface_type(ifname)
                interfaces[ifname] = {
                    "name": ifname,
                    "type": iftype,
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [{"name": ifname, "admin_status": True, "oper_status": True}],
                }
                continue
            match = self.rx_iface_mac.search(block)
            if match and match.group("mac") != "00:00:00:00:00:00":
                interfaces[ifname]["mac"] = match.group("mac")
            match = self.rx_iface_mtu.search(block)
            if match:
                interfaces[ifname]["mtu"] = match.group("mtu")
            match = self.rx_iface_ifindex.search(block)
            if match:
                interfaces[ifname]["ifindex"] = match.group("ifindex")
            l3_addresses = []
            for l3 in self.rx_iface_l3_address1.finditer(block):
                # format inet 224.0.0.1  mask 240.0.0.0
                address = l3.group("address")
                netmask = str(IPv4.netmask_to_len(l3.group("netmask")))
                l3_addresses += ["%s/%s" % (address, netmask)]
            for l3 in self.rx_iface_l3_address2.finditer(block):
                # format      Internet address: 192.168.20.1
                #      Broadcast address: 192.168.20.255
                #      Netmask 0xffffff00 Subnetmask 0xffffff00
                address = l3.group("address")
                netmask = format(int(l3.group("netmask"), 16), "b").count("1")
                l3_addresses += ["%s/%s" % (address, netmask)]
            if l3_addresses:
                interfaces[ifname]["subinterfaces"][0]["ipv4_addresses"] = l3_addresses
                interfaces[ifname]["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
        return interfaces

    def execute_snmp(self, **kwargs):
        interfaces = {}
        for oid, name in self.snmp.getnext(mib["IF-MIB::ifDescr"]):
            ifindex = int(oid.split(".")[-1])
            match = self.rx_snmp_iface.match(name)
            if match:
                ifname = "%(shelf)s/%(slot)s/%(port)s/%(mani)s" % match.groupdict()
            else:
                ifname = name
            if ifname not in interfaces:
                interfaces[ifname] = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": True,
                    "oper_status": True,
                    "ifindex": ifindex,
                    "subinterfaces": [
                        {
                            "name": "%s.%s:%s" % (ifname, 0, 0),
                            "type": "physical",
                            "admin_status": True,
                            "oper_status": True,
                            "enabled_afi": ["ATM"],
                        }
                    ],
                }
        interfaces.update(self.get_l3_interfaces())
        return [{"interfaces": sorted(six.itervalues(interfaces), key=lambda x: x["name"])}]

    def execute_cli(self, **kwargs):
        # "EXISTSH ALL"
        interfaces = {}
        # boards = self.profile.get_boards(self)
        try:
            v = self.cli("ginv all", cached=True)
        except self.CLISyntaxError:
            raise NotImplementedError
        for line in self.rx_table_spliter.split(v):
            if not line.startswith("|"):
                continue
            row = [x.strip() for x in line.strip("|\n").split("|")]
            if row[0] == "SH":
                # header
                continue
            shelf, slot, port, mani, _, sw_ver, boot_ver, hw_ver, serial, _, _ = row
            if int(port) == 0:
                continue
            # detail = self.cli("ginv %s %s %s %s" % (shelf, slot, port, mani))
            ifname = "%s/%s/%s/%s" % (shelf, slot, port, mani)
            interfaces[ifname] = {
                "name": ifname,
                "type": "physical",
                "admin_status": True,
                "oper_status": True,
                # "ifindex": None,
                "subinterfaces": [],  # "enabled_afi": ["ATM"],
            }
            interfaces[ifname]["subinterfaces"] += [
                {
                    "name": "%s.%s:%s" % (ifname, 0, 0),
                    "type": "physical",
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": ["ATM"],
                    # "ifindex": None,
                }
            ]
        interfaces.update(self.get_l3_interfaces())
        return [{"interfaces": sorted(six.itervalues(interfaces), key=lambda x: x["name"])}]
