# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# APC.AOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC
from noc.lib.text import parse_kv


class Script(BaseScript):
    """
    """
    name = "APC.AOS.get_chassis_id"
    interface = IGetChassisID

    OIDS_CHECK = ["1.3.6.1.2.1.2.2.1.6.2"]

    def execute_cli(self):
        v = self.cli("about", cached=True)

        s = parse_kv({"mac address": "mac"}, v)
        if s:
            s = s["mac"].replace(" ", ":")
            return {"first_chassis_mac": MAC(s), "last_chassis_mac": MAC(s)}
        else:
            raise self.NotSupportedError
