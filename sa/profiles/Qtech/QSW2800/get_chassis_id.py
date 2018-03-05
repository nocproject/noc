# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2800.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Qtech.QSW2800.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(
        r"^\s*\S+\s+MAC\s+(?P<mac>\S+)$",
        re.MULTILINE | re.IGNORECASE)
    rx_mac_old = re.compile(
        r"^\d+\s+(?P<mac>\S+)\s+\S+\s+\S+\s+CPU$",
        re.MULTILINE | re.IGNORECASE)

    def execute_cli(self):
        r = []
        v = self.scripts.get_version()
        if v["version"].startswith("7") or self.match_version(version__gte="6.3.100.12"):
            macs = []
            cmd = self.cli("show version")
            for match in self.rx_mac.finditer(cmd):
                macs += [match.group("mac")]
            macs.sort()
            r = [{
                "first_chassis_mac": f,
                "last_chassis_mac": t
            } for f, t in self.macs_to_ranges(macs)]
        if not r:
            # If not SystemID in version command
            vlan_cmd = self.cli("show mac-address-table static | i CPU")
            match = self.rx_mac_old.match(vlan_cmd)
            if match:
                vlan_mac = match.group("mac")
            iface_cmd = self.cli("show interface | i address is")
            iface_match = iface_cmd.splitlines()[0].split()[-1]
            return {
                "first_chassis_mac": vlan_mac,
                "last_chassis_mac": iface_match
            }

        return r
