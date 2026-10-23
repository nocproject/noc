# ----------------------------------------------------------------------
# Raisecom.RCIOS.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "Raisecom.RCIOS.get_version"
    interface = IGetVersion
    cache = True

    kv_map = {
        "version": "version",
        "device": "platform",
        "serial number": "serial",
        "bootrom version": "bootprom",
        "ios version": "hw_version",
    }

    def execute(self):
        v = self.cli("show version", cached=True)
        r = parse_kv(self.kv_map, v, sep=":")
        return {
            "vendor": "Raisecom",
            "platform": r["platform"],
            "version": r["version"],
            "attributes": {
                "Serial Number": r["serial"],
                "Boot PROM": r["bootprom"],
                "HW version": r["hw_version"],
            },
        }
