# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.Comware.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "HP.Comware.get_version"
    cache = True
    interface = IGetVersion

    rx_version_HP = re.compile(r"^Comware Software, Version (?P<version>.+)$", re.MULTILINE)
    rx_platform_HP = re.compile(
        r"^HP.*?\s(?P<platform>[A-Z,0-9a-z\-]+).*?.*?(Switch|uptime)", re.MULTILINE
    )
    rx_devinfo = re.compile(
        r"^Slot 1:\nDEVICE_NAME\s+:\s+(?P<platform>[A-Z,0-9a-z\-]+)\s+.+?\n"
        r"DEVICE_SERIAL_NUMBER\s+:\s+(?P<serial>\S+)\n"
    )

    def execute_cli(self, **kwargs):
        platform = "Comware"
        version = "Unknown"

        v = self.cli("display version")
        match = self.rx_version_HP.search(v)
        s = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum.37"]) if self.has_snmp() else None
        if match:
            version = match.group("version")
        match = self.rx_platform_HP.search(v)
        if match:
            platform = match.group("platform")
        if platform == "Comware":
            try:
                v = self.cli("display device manuinfo")
                match = self.rx_devinfo.search(v)
                if match:
                    platform = match.group("platform")
                    s = match.group("serial")
            except Exception:
                pass
        r = {"vendor": "HP", "platform": platform, "version": version, "attributes": {}}
        if not s and self.has_snmp():
            s = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum.1"])
            if not s:
                s = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum.2"])
        if s:
            r["attributes"]["Serial Number"] = s
        return r
