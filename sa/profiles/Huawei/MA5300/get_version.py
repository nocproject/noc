# ---------------------------------------------------------------------
# Huawei.MA5300.get_version
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Huawei.MA5300.get_version"
    cache = True
    interface = IGetVersion
    always_prefer = "S"

    rx_platform = re.compile(r"SmartAX (?P<platform>\S+) \S+")
    rx_ver = re.compile(r"Version (?P<version>\S+)")

    def execute_snmp(self, **kwargs):
        # slot number
        slots_count = self.snmp.get(mib["HUAWEI-DEVICE-MIB::hwSlots", 0])
        version = self.snmp.get(mib["HUAWEI-DEVICE-MIB::hwSysVersion", 0])
        platform = self.snmp.get(mib["HUAWEI-DEVICE-MIB::hwFrameDesc", 0])
        if slots_count == 8:
            platform = "MA5303"
        elif slots_count == 16:
            platform = "MA5300"
        return {"vendor": "Huawei", "platform": platform, "version": version}

    def execute_cli(self, **kwargs):
        v = self.cli("show version", cached=True)
        match = self.re_search(self.rx_ver, v)
        version = match.group("version")
        match = self.re_search(self.rx_platform, v)
        platform = match.group("platform")
        return {"vendor": "Huawei", "platform": platform, "version": version}
