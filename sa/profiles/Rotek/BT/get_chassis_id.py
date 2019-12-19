# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rotek.RTBS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.http.client import fetch_sync


class Script(BaseScript):
    name = "Rotek.BT.get_chassis_id"
    cache = True
    interface = IGetChassisID
    rx_mac = re.compile(r"MAC(?:\S+:|:)\s(?P<mac>\S+)<", re.MULTILINE)

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                base = self.snmp.get("1.3.6.1.2.1.2.2.1.6.1")
                if base:
                    return [{"first_chassis_mac": base, "last_chassis_mac": base}]
            except self.snmp.TimeOutError:
                pass
            except self.snmp.SNMPError:
                pass

        # Fallback to CLI
        get = "http://" + self.credentials.get("address", "") + "/"
        code, header, body = fetch_sync(get, allow_proxy=False, eof_mark="</html>")
        if 200 <= code <= 299:
            match = self.rx_mac.search(body)
            if match:
                mac = (match.group("mac")).strip()
                return [{"first_chassis_mac": mac, "last_chassis_mac": mac}]
