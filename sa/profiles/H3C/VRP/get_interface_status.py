# ---------------------------------------------------------------------
# H3C.VRP.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus

rx_ifc_status = re.compile(
    r"^\s*(?P<interface>[^ ]+) current state :.*?(?P<status>up|down)", re.IGNORECASE
)
rx_ifc_block = re.compile(
    r"Interface\s+(PHY|Physical)\s+Protocol[^\n]+\n(?P<block>.*)$",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)
rx_ifc_br_status = re.compile(
    r"^\s*(?P<interface>[^ ]+)\s+(?P<status>up|down|\*down).*$", re.IGNORECASE
)


class Script(BaseScript):
    name = "H3C.VRP.get_interface_status"
    interface = IGetInterfaceStatus

    def execute(self, interface=None):
        if self.has_snmp():
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
                for i, n, s in self.snmp.join(["1.3.6.1.2.1.31.1.1.1.1", "1.3.6.1.2.1.2.2.1.8"]):
                    # ifOperStatus up(1)
                    if interface and interface == self.profile.convert_interface_name(n):
                        return [{"interface": n, "status": int(s) == 1}]
                    r += [{"interface": n, "status": int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        r = []
        #
        # VRP3 style
        #
        if self.is_version_3x:
            for ll in self.cli("display interface").splitlines():
                if ll.find(" current state :") != -1 and ll.find("Line protocol ") == -1:
                    match_int = rx_ifc_status.match(ll)
                    if match_int:
                        iface = match_int.group("interface")
                        if interface and interface == self.profile.convert_interface_name(iface):
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
            match = rx_ifc_block.search(cli)
            if match:
                for ll in match.group("block").splitlines():
                    match_int = rx_ifc_br_status.match(ll)
                    if match_int:
                        iface = match_int.group("interface")
                        if interface and interface == self.profile.convert_interface_name(iface):
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
