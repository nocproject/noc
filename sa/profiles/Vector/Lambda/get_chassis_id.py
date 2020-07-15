# ---------------------------------------------------------------------
# Vector.Lambda.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Vector.Lambda.get_chassis_id"
    cache = True
    interface = IGetChassisID

    SNMP_GET_OIDS = {"SNMP": ["1.3.6.1.4.1.5591.1.3.2.7.0"]}

    rx_mac = re.compile(r"^MAC\s+addr\s+:\s+(?P<mac>\S+)", re.MULTILINE)

    def execute(self, **kwargs):
        if self.is_vectrar2d2:
            self.SNMP_GET_OIDS["SNMP"] = ["1.3.6.1.4.1.17409.1.3.2.1.1.1.0"]
        elif self.is_sysid_support:
            self.SNMP_GET_OIDS["SNMP"] = ["1.3.6.1.4.1.34652.2.11.5.1.0"]
        return super().execute(**kwargs)

    def execute_cli(self, **kwargs):
        cmd = self.cli("net dump")
        match = self.rx_mac.search(cmd)
        if match:
            mac = match.group("mac")
        else:
            raise self.NotSupportedError
        return [{"first_chassis_mac": mac, "last_chassis_mac": mac}]
