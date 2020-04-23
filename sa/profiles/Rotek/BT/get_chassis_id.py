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
from noc.core.http.client import fetch_sync
from noc.core.mib import mib


class Script(BaseScript):
    name = "Rotek.BT.get_chassis_id"
    cache = True
    interface = IGetChassisID
    rx_mac = re.compile(r"MAC(?:\S+:|:)\s(?P<mac>\S+)<", re.MULTILINE)

    SNMP_GET_OIDS = {"SNMP": mib["IF-MIB::ifPhysAddress", 1]}

    always_prefer = "S"

    def execute_cli(self, **kwargs):
        # Fallback to CLI
        get = "http://" + self.credentials.get("address", "") + "/"
        code, header, body = fetch_sync(get, allow_proxy=False, eof_mark="</html>")
        if 200 <= code <= 299:
            match = self.rx_mac.search(body)
            if match:
                mac = (match.group("mac")).strip()
                return [{"first_chassis_mac": mac, "last_chassis_mac": mac}]
