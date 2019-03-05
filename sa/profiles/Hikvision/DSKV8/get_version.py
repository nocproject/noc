# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Hikvision.DSKV8.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
import xml.etree.ElementTree as ElementTree
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Hikvision.DSKV8.get_version"
    interface = IGetVersion
    cache = True

    rx_date = re.compile(r"(?P<yy>\d\d)(?P<mm>\d\d)(?P<dd>\d\d)")

    def execute(self):
        v = self.http.get("/ISAPI/System/deviceInfo/capabilities", json=False, cached=True, use_basic=True)
        root = ElementTree.fromstring(v)
        for child in root:
            key = child.tag.split("}")[1][0:]
            if key == "model":
                platform = child.text
            elif key == "serialNumber":
                serial = child.text
            elif key == "firmwareVersion":
                version = child.text
            elif key == "firmwareReleasedDate":
                build = child.text
                match = self.rx_date.search(build)
                build = "20%s-%s-%s" % (match.group("yy"), match.group("mm"), match.group("dd"))

        return {
            "vendor": 'Hikvision',
            "platform": platform,
            "version": version,
            "attributes": {
                "Serial Number": serial,
                "build": build
            }
        }
