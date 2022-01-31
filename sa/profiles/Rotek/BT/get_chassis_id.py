# ---------------------------------------------------------------------
# Rotek.RTBS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mib import mib


class Script(BaseScript):
    name = "Rotek.BT.get_chassis_id"
    cache = True
    interface = IGetChassisID
    rx_mac = re.compile(r"MAC(?:\S+:|:)\s(?P<mac>\S+)<", re.MULTILINE)

    SNMP_GET_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress", 1]]}

    always_prefer = "S"

    def execute_cli(self, **kwargs):
        mac = None
        if self.is_4250lsr:
            v = self.http.get("/info.cgi?_", json=True, cached=True, eof_mark=b"}")
            mac = v["macaddr"]
        elif self.is_6037_v1:
            v = self.http.get("/", cached=True, eof_mark=b"</html>")
            match = self.rx_mac.search(v)
            mac = match.group("mac")
        if not mac:
            raise NotImplementedError
        return [{"first_chassis_mac": mac, "last_chassis_mac": mac}]
