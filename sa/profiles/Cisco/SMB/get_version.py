# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.SMB.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Cisco.SMB.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^SW version\s+(?P<version>[^\s,]+).+"
        r"Boot version\s+(?P<bootver>[^\s,]+).+"
        r"HW version\s+(?P<hwver>[^\s]+)", re.MULTILINE | re.DOTALL)
    rx_ver2 = re.compile(
        r"^Active-image: flash://system/images/(?P<image>\S+bin)\s*\n"
        r"^\s+Version: (?P<version>\S+)", re.MULTILINE)
    rx_platform = re.compile(
        r"System Description:\s+(?P<platform>.+)\n", re.IGNORECASE)
    rx_inventory = re.compile(
        r"^PID:\s*(?P<pid>\S+)\s+VID:\s*\S+\s+SN:\s*(?P<sn>\S+)\s*$",
        re.MULTILINE)

    def execute(self):
        s = self.cli("show system", cached=True)
        pmatch = self.rx_platform.search(s)
        v = self.cli("show version", cached=True)
        vmatch = self.rx_ver.search(v)
        if not vmatch:
            vmatch = self.rx_ver2.search(v)
            if vmatch:
                return {
                    "vendor": "Cisco",
                    "platform": pmatch.group("platform"),
                    "version": vmatch.group("version"),
                    "attributes": {
                        "image": vmatch.group("image"),
                    }
                }
        try:
            i = self.cli("show inventory", cached=True)
            imatch = self.rx_inventory.search(i)
            pid = imatch.group("pid")
            sn = imatch.group("sn")
        except self.CLISyntaxError:
            pid = None
            sn = None
        return {
            "vendor": "Cisco",
            "platform": pmatch.group("platform"),
            "version": vmatch.group("version"),
            "attributes": {
                "Boot PROM": vmatch.group("bootver"),
                "HW version": vmatch.group("hwver"),
                "Serial Number": sn,
                "pid": pid
            }
        }
