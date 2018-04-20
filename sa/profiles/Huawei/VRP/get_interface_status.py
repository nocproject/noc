# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Huawei.VRP.get_interface_status
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfacestatus import IGetInterfaceStatus
import re

rx_ifc_status = re.compile(
    r"^\s*(?P<interface>[^ ]+) current state\s*:.*?(?P<status>up|down)",
=======
##----------------------------------------------------------------------
## Huawei.VRP.get_interface_status
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaceStatus
import re

rx_ifc_status = re.compile(
    r"^\s*(?P<interface>[^ ]+) current state :.*?(?P<status>up|down)",
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    re.IGNORECASE)
rx_ifc_block = re.compile(
    r"Interface\s+(PHY|Physical)\s+Protocol[^\n]+\n(?P<block>.*)$",
    re.MULTILINE | re.DOTALL | re.IGNORECASE)
rx_ifc_br_status = re.compile(
    r"^\s*(?P<interface>[^ ]+)\s+(?P<status>up|down|\*down).*$", re.IGNORECASE)


<<<<<<< HEAD
class Script(BaseScript):
    name = "Huawei.VRP.get_interface_status"
    interface = IGetInterfaceStatus

    def execute(self, interface=None):
        if self.has_snmp():
=======
class Script(NOCScript):
    name = "Huawei.VRP.get_interface_status"
    implements = [IGetInterfaceStatus]

    def execute(self, interface=None):
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                # Get interface status
                r = []
                # IF-MIB::ifName, IF-MIB::ifOperStatus
<<<<<<< HEAD
                for i, n, s in self.snmp.join([
                    "1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.2.2.1.8"
                ]):
=======
                for n, s in self.snmp.join_tables(
                        "1.3.6.1.2.1.31.1.1.1.1",
                        "1.3.6.1.2.1.2.2.1.8",
                        bulk=True
                ):
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    # ifOperStatus up(1)
                    if (interface and
                                interface == self.profile.convert_interface_name(n)):
                        return [{"interface": n, "status": int(s) == 1}]
                    r += [{"interface": n, "status": int(s) == 1}]
                return r
            except self.snmp.TimeOutError:
                pass
        # Fallback to CLI
        r = []
        ##
        ## VRP3 style
        ##
<<<<<<< HEAD
        version = self.profile.fix_version(self.scripts.get_version())
        if version.startswith("3."):
            for l in self.cli("display interface").splitlines():
                if ((l.find(" current state :") != -1 \
                or l.find(" current state:") != -1) \
=======
        if self.match_version(version__startswith="3."):
            for l in self.cli("display interface").splitlines():
                if (l.find(" current state :") != -1 \
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                and l.find("Line protocol ") == -1):
                    match_int = rx_ifc_status.match(l)
                    if match_int:
                        iface = match_int.group("interface")
                        if (interface and
                                    interface == self.profile.convert_interface_name(iface)):
                            return [{
                                "interface": iface,
                                "status": match_int.group("status").lower() == "up"
                            }]
                        r += [{
                            "interface": iface,
                            "status": match_int.group("status").lower() == "up"
                        }]
        ##
        ## Other (VRP5 style)
        ##
        else:
            cli = self.cli("display interface brief", cached=True)
            match = rx_ifc_block.search(cli)
            if match:
                for l in match.group("block").splitlines():
                    match_int = rx_ifc_br_status.match(l)
                    if match_int:
                        iface = match_int.group("interface")
                        if (interface and
                                    interface == self.profile.convert_interface_name(iface)):
                            return [{
                                "interface": iface,
                                "status": match_int.group("status").lower() == "up"
                            }]
                        r += [{
                            "interface": iface,
                            "status": match_int.group("status").lower() == "up"
                        }]
        return r
