# ---------------------------------------------------------------------
# CData.xPON.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "CData.xPON.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"ifIndex:\s+(?P<snmp_ifindex>\d+), linkStatus: (?P<oper_status>\d+), "
        r"portName:\s+(?P<ifname>\S+),"
    )
    rx_mgmt = re.compile(
        r"^Status : (?P<oper_status>\S+)\s*\n"
        r"^The Maximum Transmit Unit is (?P<mtu>\d+) bytes\s*\n"
        r"^Internet Address is (?P<ip>\S+), netmask (?P<mask>\S+)\s*\n"
        r"^Hardware address is (?P<mac>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_vlanif = re.compile(
        r"^Description : Inband interface (?P<ifname>vlanif\d+) is (?P<oper_status>\S+), "
        r"administrator status is (?P<admin_status>\S+)\s*\n"
        r"^The Maximum Transmit Unit is (?P<mtu>\d+) bytes\s*\n"
        r"^Internet Address is (?P<ip>\S+), netmask (?P<mask>\S+)\s*\n"
        r"^Hardware address is (?P<mac>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_vlanid = re.compile(r"[Vv]lanif(?P<vlan_id>\d+)")

    def execute_cli(self, **kwargs):
        interfaces = []
        with self.configure():
            v = self.cli("show lacp system port")
            for match in self.rx_port.finditer(v):
                iface = {
                    "name": match.group("ifname"),
                    "type": "physical",
                    "snmp_ifindex": match.group("snmp_ifindex"),
                    "admin_status": True,
                    "oper_status": match.group("oper_status").lower() == "1",
                    "enabled_protocols": [],
                    "subinterfaces": [],
                }
                sub = {
                    "name": match.group("ifname"),
                    "admin_status": True,
                    "oper_status": match.group("oper_status").lower() == "1",
                    "enabled_afi": ["BRIDGE"],
                    "enabled_protocols": [],
                }
                iface["subinterfaces"] += [sub]
                interfaces += [iface]
            try:
                v = self.cli("show interface vlanif")
                for match in self.rx_vlanif.finditer(v):
                    ifname = match.group("ifname")
                    ip_address = match.group("ip")
                    ip_mask = match.group("mask")
                    ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_mask))
                    vlan_id = self.rx_vlanid.search(ifname).group("vlan_id")
                    iface = {
                        "name": ifname,
                        "type": "SVI",
                        "admin_status": match.group("admin_status").lower() == "up",
                        "oper_status": match.group("oper_status").lower() == "up",
                        "mac": match.group("mac"),
                        "subinterfaces": [
                            {
                                "name": ifname,
                                "admin_status": match.group("admin_status").lower() == "up",
                                "oper_status": match.group("oper_status").lower() == "up",
                                "mtu": match.group("mtu"),
                                "enabled_afi": ["IPv4"],
                                "ipv4_addresses": [ip_address],
                                "vlan_id": vlan_id,
                            }
                        ],
                    }
                    interfaces += [iface]
            except self.CLISyntaxError:
                pass

            try:
                v = self.cli("show interface mgmt")
                match = self.rx_mgmt.search(v)
                if match:
                    ip_address = match.group("ip")
                    ip_mask = match.group("mask")
                    ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_mask))
                    iface = {
                        "name": "mgmt",
                        "type": "management",
                        "admin_status": True,
                        "oper_status": match.group("oper_status").lower() == "enable",
                        "mac": match.group("mac"),
                        "subinterfaces": [
                            {
                                "name": "mgmt",
                                "admin_status": True,
                                "oper_status": match.group("oper_status").lower() == "enable",
                                "mtu": match.group("mtu"),
                                "enabled_afi": ["IPv4"],
                                "ipv4_addresses": [ip_address],
                            }
                        ],
                    }
                    interfaces += [iface]
            except self.CLISyntaxError:
                pass

        return [{"interfaces": interfaces}]
