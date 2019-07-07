# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Hikvision.DSKV8.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import xml.etree.ElementTree as ElementTree

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Hikvision.DSKV8.get_chassis_id"
    cache = True
    interface = IGetChassisID

    def execute(self):
        v = self.http.get("/ISAPI/System/deviceInfo", cached=True, use_basic=True)
        v = v.replace("\n", "")
        root = ElementTree.fromstring(v)
        for child in root:
            key = child.tag.split("}")[1][0:]
            if key == "macAddress":
                mac = child.text
                break

        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
