# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.WLC.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib

rx_ver = re.compile(r"^Product Version\.+\s+(?P<version>\S+)", re.MULTILINE | re.DOTALL)
rx_inv = re.compile(r"^PID:\s+(?P<platform>\S+)\,", re.MULTILINE | re.DOTALL)


class Script(BaseScript):
    name = "Cisco.WLC.get_version"
    cache = True
    interface = IGetVersion

    def execute_cli(self, **kwargs):
        v = self.cli("show sysinfo")
        match = rx_ver.search(v)
        version = match.group("version")
        v = self.cli("show inventory")
        match = rx_inv.search(v)
        platform = match.group("platform")
        return {"vendor": "Cisco", "platform": platform, "version": version}

    def execute_snmp(self, **kwargs):
        version = self.snmp.get(mib["AIRESPACE-SWITCHING-MIB::agentInventoryProductVersion", 0])
        platform = self.snmp.get(mib["AIRESPACE-SWITCHING-MIB::agentInventoryMachineModel", 0])
        return {"vendor": "Cisco", "platform": platform, "version": version}
