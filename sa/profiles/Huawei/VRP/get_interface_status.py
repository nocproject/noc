# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus


class Script(BaseScript):
    name = "Huawei.VRP.get_interface_status"
    interface = IGetInterfaceStatus

    rx_ifc_status = re.compile(
        r"^\s*(?P<interface>[^ ]+) current state\s*:.*?(?P<status>up|down)", re.IGNORECASE
    )
    rx_ifc_block = re.compile(
        r"Interface\s+(PHY|Physical)\s+Protocol[^\n]+\n(?P<block>.*)$",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    rx_ifc_br_status = re.compile(
        r"^\s*(?P<interface>[^ ]+)\s+(?P<status>up|down|\*down).*$", re.IGNORECASE
    )

    def execute_snmp(self, interface=None, **kwargs):
        # Get interface status
        r = []
        # IF-MIB::ifName, IF-MIB::ifOperStatus
        for i, n, s in self.snmp.join(["1.3.6.1.2.1.31.1.1.1.1", "1.3.6.1.2.1.2.2.1.8"]):
            iface = self.profile.convert_interface_name(n)
            # ifOperStatus up(1)
            if interface and interface == iface:
                return [{"interface": iface, "status": int(s) == 1}]
            r += [{"interface": iface, "status": int(s) == 1}]
        return r

    def execute_cli(self, interface=None):
        # Fallback to CLI
        r = []
        #
        # VRP3 style
        #
        if self.is_kernel_3 or self.is_bad_platform:
            for line in self.cli("display interface").splitlines():
                if (
                    line.find(" current state :") != -1 or line.find(" current state:") != -1
                ) and line.find("Line protocol ") == -1:
                    match_int = self.rx_ifc_status.match(line)
                    if match_int:
                        iface = self.profile.convert_interface_name(match_int.group("interface"))
                        if interface and interface == iface:
                            return [
                                {
                                    "interface": iface,
                                    "status": match_int.group("status").lower() == "up",
                                }
                            ]
                        r += [
                            {
                                "interface": iface,
                                "status": match_int.group("status").lower() == "up",
                            }
                        ]
        #
        # Other (VRP5 style)
        #
        else:
            cli = self.cli("display interface brief", cached=True)
            match = self.rx_ifc_block.search(cli)
            if match:
                for line in match.group("block").splitlines():
                    match_int = self.rx_ifc_br_status.match(line)
                    if match_int:
                        iface = self.profile.convert_interface_name(match_int.group("interface"))
                        if interface and interface == iface:
                            return [
                                {
                                    "interface": iface,
                                    "status": match_int.group("status").lower() == "up",
                                }
                            ]
                        r += [
                            {
                                "interface": iface,
                                "status": match_int.group("status").lower() == "up",
                            }
                        ]
        return r
