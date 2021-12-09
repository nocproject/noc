# ----------------------------------------------------------------------
# NSN.TIMOS.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "NSN.TIMOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    SNMP_GETNEXT_OIDS = {"SNMP": ["1.3.6.1.4.1.6527.3.1.2.2.1.3.1.15"]}

    rx_id = re.compile(r"^\s*Base MAC address\s*:\s*(?P<id>\S+)", re.IGNORECASE | re.MULTILINE)

    def execute_cli(self):
        r = []
        v = self.cli("show chassis")
        match = self.re_search(self.rx_id, v)
        r += [{"first_chassis_mac": match.group("id"), "last_chassis_mac": match.group("id")}]
        try:
            v = self.cli("show card detail")
            for match in self.rx_id.finditer(v):
                r += [
                    {"first_chassis_mac": match.group("id"), "last_chassis_mac": match.group("id")}
                ]
        except self.CLISyntaxError:
            pass
        return r
