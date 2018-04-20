# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
import re


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_chassis_id"
    interface = IGetChassisID
    rx_ver = re.compile(r"^Hardware is\s+VLAN, address is (?P<id>\S+)\s+",
                        re.IGNORECASE | re.MULTILINE)
    rx_mac = re.compile(r"^\s+Chassis\s+ID\s+:\s+(?P<mac>\S+)",
                             re.IGNORECASE | re.MULTILINE)
    rx_vlan_int = re.compile(r"^VLAN (?P<vlan_id>\d+)\s+",
                             re.IGNORECASE | re.MULTILINE)

    def execute(self):
        macs = []
        match = self.re_search(
            self.rx_mac, self.cli("show lldp local-information global"))
        macs = [match.group("mac")]
        try:
            v = self.cli("show ip interface brief")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_vlan_int.finditer(v):
            vlan_id = match.group("vlan_id")
            c = "show interface vlan %s | include Hardware" % vlan_id
            match2 = self.re_search(self.rx_ver, self.cli(c))
            m = match2.group("id")
            if not m in macs:
                macs += [m]
        macs.sort()
        return [{
            "first_chassis_mac": f,
            "last_chassis_mac": t
        } for f, t in self.macs_to_ranges(macs)]
=======
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
import re


class Script(NOCScript):
    name = "DLink.DxS_Cisco_CLI.get_chassis_id"
    implements = [IGetChassisID]
    rx_ver = re.compile(r"^Hardware is  VLAN, address is (?P<id>\S+)\s+",
                        re.IGNORECASE | re.MULTILINE)
    rx_mac_from = re.compile(r"^\s+Chassis\s+ID\s+:\s+(?P<mac_from>\S+)",
                             re.IGNORECASE | re.MULTILINE)

    def execute(self):
        match1 = self.re_search(
            self.rx_mac_from, self.cli("show lldp local-information global"))
        mac_from = match1.group("mac_from")
        match = self.re_search(self.rx_ver, self.cli("show interfaces vlan 1"))
        mac_to = match.group("id")
        return {
            "first_chassis_mac": mac_from,
            "last_chassis_mac": mac_to
        }
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
