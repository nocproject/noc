# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DCN.DCWL.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "DCN.DCWL.get_version"
    cache = True
    interface = IGetVersion

    def execute_snmp(self, **kwargs):
        oids = {
            "serial": "1.3.6.1.4.1.6339.100.1.1.1.0",
            "platform": "1.3.6.1.4.1.6339.100.1.1.2.0",
            "version": "1.3.6.1.4.1.6339.100.1.1.4.0",
        }
        try:
            r = self.snmp.get(oids)
        except Exception:
            raise NotImplementedError
        return {
            "vendor": "DCN",
            "platform": r["platform"],
            "version": r["version"],
            "attributes": {"HW version": "hwversion", "Serial Number": r["serial"]},
        }

    def execute_cli(self, **kwargs):
        r = []
        c = self.cli("get device-info", cached=True)
        for line in c.splitlines():
            r = line.split(" ", 1)
            if r[0] == "device-name":
                platform = r[1].strip()
            if r[0] == "version-id":
                hwversion = r[1].strip()
        d = self.cli("get system detail", cached=True)
        for line in d.splitlines():
            r = line.split(" ", 1)
            if r[0] == "version":
                version = r[1].strip()
            if r[0] == "serial-number":
                sn = r[1].strip()
        return {
            "vendor": "DCN",
            "platform": platform,
            "version": version,
            "attributes": {"HW version": hwversion, "Serial Number": sn},
        }
