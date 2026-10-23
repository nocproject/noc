# ---------------------------------------------------------------------
# Mellanox.Cumulus.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Mellanox.Cumulus.get_version"
    interface = IGetVersion
    cache = True

    def execute_cli(self):
        v = self.cli("decode-syseeprom", cached=True)
        for i in parse_table(v, max_width=250):
            if i[0] == "Part Number":
                platform = i[3]
            elif i[0] == "Serial Number":
                serial = i[3]
            elif i[0] == "Device Version":
                hardware = i[3]
            elif i[0] == "ONIE Version":
                version = i[3]
        return {
            "vendor": "Mellanox",
            "platform": platform,
            "version": version,
            "attributes": {
                "HW version": hardware,
                "Serial Number": serial,
            },
        }
