# ---------------------------------------------------------------------
# HP.Aruba.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.text import parse_kv
from noc.core.mib import mib


class Script(BaseScript):
    name = "HP.Aruba.get_version"
    cache = True
    interface = IGetVersion

    parse_kv_map = {
        "vendor": "vendor",
        "product name": "product_name",
        "arubaos-cx version": "version",
        "chassis serial nbr": "serial",
    }

    def execute_cli(self):
        v = self.cli("show system", cached=True)
        r = parse_kv(self.parse_kv_map, v)
        return {
            "vendor": "Aruba",
            "platform": r["product_name"],
            "version": r["version"],
        }

    def execute_snmp(self, **kwargs):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
        v = v.split()
        return {
            "vendor": "Aruba",
            "platform": " ".join(v[1:-1]),
            "version": v[-1],
        }
