# ----------------------------------------------------------------------
# Planar.SDO3000.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Planar.SDO3000.get_interfaces"
    interface = IGetInterfaces

    rx_ipaddr = re.compile(r"Current IP address:\s+(?P<ip>\S+)")
    rx_mask = re.compile(r"\s+<3>\. Subnet mask:\s+(?P<mask>\S+)\s+")
    rx_ports = re.compile(r"Input (?P<port>\d+) optical power")

    def get_phys_ports(self):
        """
        Return optical and RF ports
        :return:
        :rtype: list
        """
        ports = [
            {
                "name": "Input 1",
                "admin_status": True,
                "oper_status": True,
                "type": "physical",
                "subinterfaces": [],
            }
        ]
        plat = self.scripts.get_version()["platform"]
        if plat == "SDO3002":
            ports += [
                {
                    "name": "Input 2",
                    "admin_status": True,
                    "oper_status": True,
                    "type": "physical",
                    "subinterfaces": [],
                }
            ]
        return ports

    def execute_cli(self, **kwargs):
        iface = []
        cmd = self.scripts.get_chassis_id()
        mac = cmd[0]["first_chassis_mac"]
        self.cli("4")  # Enter Configuration menu
        cmd = self.cli("1")  # Enter Network submenu
        match = self.rx_ipaddr.search(cmd)
        ipaddr = match.group("ip")
        match = self.rx_mask.search(cmd)
        # netmask may be wrong when DHCP is used!
        mask = match.group("mask")
        ip = IPv4(ipaddr, mask)
        iface += [
            {
                "name": "Output",
                "admin_status": True,
                "oper_status": True,
                "type": "physical",
                "subinterfaces": [],
            },
            {
                "name": "mgmt",
                "admin_status": True,
                "oper_status": True,
                "type": "physical",
                "hints": ["noc::interface::role::mgmt"],
                "mac": mac,
                "subinterfaces": [
                    {
                        "name": "mgmt",
                        "enabled_afi": ["IPv4"],
                        "mac": mac,
                        "ipv4_addresses": [ip],
                        "admin_status": True,
                        "oper_status": True,
                    }
                ],
            },
        ]
        iface += self.get_phys_ports()
        return [{"interfaces": iface}]

    def execute_snmp(self, **kwargs):
        cmd = self.scripts.get_chassis_id()
        mac = cmd[0]["first_chassis_mac"]
        ipaddr = self.snmp.get("1.3.6.1.4.1.32108.1.7.4.1.1.0")  # PLANAR-sdo3002-MIB::currentIP
        # netmask may be wrong when DHCP is used!
        mask = self.snmp.get(
            "1.3.6.1.4.1.32108.1.7.4.1.4.0"
        )  # PLANAR-sdo3002-MIB::staticSubnetMask
        ip = IPv4(ipaddr, mask)
        ifaces = [
            {
                "name": "Output",
                "admin_status": True,
                "oper_status": True,
                "type": "physical",
                "subinterfaces": [],
            },
            {
                "name": "mgmt",
                "admin_status": True,
                "oper_status": True,
                "type": "physical",
                "hints": ["noc::interface::role::mgmt"],
                "mac": mac,
                "subinterfaces": [
                    {
                        "name": "mgmt",
                        "enabled_afi": ["IPv4"],
                        "mac": mac,
                        "ipv4_addresses": [ip],
                        "admin_status": True,
                        "oper_status": True,
                    }
                ],
            },
        ]
        ifaces += self.get_phys_ports()
        return [{"interfaces": ifaces}]
