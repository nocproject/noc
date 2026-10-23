# ---------------------------------------------------------------------
# Hikvision.DSKV8.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from xml.etree import ElementTree

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Hikvision.DSKV8.get_version"
    interface = IGetVersion
    cache = True

    rx_date = re.compile(r"(?P<yy>\d\d)(?P<mm>\d\d)(?P<dd>\d\d)")

    def execute(self):
        ns = {
            "isapi": "http://www.isapi.org/ver20/XMLSchema",
            "std-cgi": "http://www.std-cgi.com/ver20/XMLSchema",
            "hikvision": "http://www.hikvision.com/ver20/XMLSchema",
        }
        v = self.http.get("/ISAPI/System/deviceInfo", cached=True, use_basic=True)
        v = v.replace("\n", "")
        if "std-cgi" in v:
            ns["ns"] = ns["std-cgi"]
        elif "www.hikvision.com" in v:
            ns["ns"] = ns["hikvision"]
        else:
            ns["ns"] = ns["isapi"]
        root = ElementTree.fromstring(v)

        return {
            "vendor": "Hikvision",
            "platform": root.find("isapi:model", ns).text,
            "version": root.find("isapi:firmwareVersion", ns).text,
            "attributes": {
                # "Boot PROM": match.group("bootprom"),
                "Build Date": root.find("isapi:firmwareReleasedDate", ns).text,
                "HW version": root.find("isapi:firmwareVersion", ns).text,
                "Serial Number": root.find("isapi:serialNumber", ns).text,
                # "Firmware Type":
            },
        }
