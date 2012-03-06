# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus
import re

rx_ifc_status = re.compile(
    r"^\s*(?P<interface>[^ ]+) current state :.*?(?P<status>up|down)",
    re.IGNORECASE)
rx_ifc_block = re.compile(
    r"Interface\s+PHY\s+Protocol[^\n]+\n(?P<block>.*)$",
    re.MULTILINE | re.DOTALL | re.IGNORECASE)
rx_ifc_br_status = re.compile(
    r"^\s*(?P<interface>[^ ]+)\s+(?P<status>up|down).*$", re.IGNORECASE)


class Script(NOCScript):
    name = "Huawei.VRP.get_interface_status"
    implements = [IGetInterfaceStatus]

    def execute(self, interface=None):
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
                for n, s in self.snmp.join_tables("1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8", bulk=True):
                    # ifOperStatus up(1)
                    r += [{"interface":n, "status":int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        r = []
        ##
        ## VRP3 style
        ##
        if self.match_version(version__startswith="3."):
            for l in self.cli("display interface").splitlines():
                if (l.find(" current state :") != -1 \
                and l.find("Line protocol ") == -1):
                    match_int = rx_ifc_status.match(l)
                    if match_int:
                        r += [{
                            "interface": match_int.group("interface"),
                            "status": match_int.group("status").lower() == "up"
                        }]
        ##
        ## Other (VRP5 style)
        ##
        else:
            cli = self.cli("display interface brief")
            match = rx_ifc_block.search(cli)
            if match:
                for l in match.group("block").splitlines():
                    match_int = rx_ifc_br_status.match(l)
                    if match_int:
                        r += [{
                            "interface": match_int.group("interface"),
                            "status": match_int.group("status").lower() == "up"
                        }]
        return r
