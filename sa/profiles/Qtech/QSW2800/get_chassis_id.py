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
    always_prefer = "S"

    rx_mac = re.compile(r"^\s*\S+\s+MAC\s+(?P<mac>\S+)$", re.MULTILINE | re.IGNORECASE)
    rx_mac_old = re.compile(r"^\d+\s+(?P<mac>\S+)\s+\S+\s+\S+\s+CPU$", re.MULTILINE | re.IGNORECASE)

    def execute_cli(self):
        macs = []
        if self.is_support_mac_version:
            cmd = self.cli("show version", cached=True)
            for match in self.rx_mac.finditer(cmd):
                macs += [match.group("mac")]
        if not macs:
            # If not SystemID in version command
            cmd = self.cli("show mac-address-table static")
            macs += self.rx_mac_old.findall(cmd)
            # For old NOC. In new collected on interface discovery
            # iface_cmd = self.cli("show interface | i address is")
            # iface_match = iface_cmd.splitlines()[0].split()[-1]

        return [
            {"first_chassis_mac": f, "last_chassis_mac": t}
            for f, t in self.macs_to_ranges(sorted(macs))
        ]
