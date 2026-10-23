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
        v = parse_kv(self.parse_kv_map, v)
        r = {
            "vendor": "Aruba",
            "platform": v["product_name"],
            "version": v["version"],
            "attributes": {},
        }
        if "serial" in v:
            r["attributes"]["Serial Number"] = v["serial"]
        return r

    def execute_snmp(self, **kwargs):
        v = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0], cached=True)
        v = v.split()
        r = {
            "vendor": "Aruba",
            "platform": " ".join(v[1:-1]),
            "version": v[-1],
            "attributes": {},
        }
        serial = self.snmp.get(mib["ENTITY-MIB::entPhysicalSerialNum", 1])
        if v:
            r["attributes"]["Serial Number"] = serial
        hw = self.snmp.get(mib["ENTITY-MIB::entPhysicalHardwareRev", 1])
        if hw:
            r["attributes"]["HW version"] = hw
        return r
