# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Hikvision.DS2CD.get_version
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
    name = "Hikvision.DS2CD.get_version"
    interface = IGetVersion
    cache = True

    rx_date = re.compile(r"(?P<yy>\d\d)(?P<mm>\d\d)(?P<dd>\d\d)")

    def execute(self):
        ns = {'ns': 'urn:psialliance-org'}
        v = self.http.get("/PSIA/System/deviceInfo", use_basic=True)
        root = ElementTree.fromstring(v)
        return {
            "vendor": 'Hikvision',
            "platform": root.find("ns:model", ns).text,
            "version": root.find("ns:firmwareVersion", ns).text,
            "attributes": {
                # "Boot PROM": match.group("bootprom"),
                "Build Date": root.find("ns:firmwareReleasedDate", ns).text,
                "HW version": root.find("ns:firmwareVersion", ns).text,
                "Serial Number": root.find("ns:serialNumber", ns).text
                # "Firmware Type":
            }
        }
