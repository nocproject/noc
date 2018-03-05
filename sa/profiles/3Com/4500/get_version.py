# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## 3Com.4500.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "3Com.4500.get_version"
    interface = IGetVersion
#    implements = [IGetVersion]
    cache = True

    rx_version_3Com = re.compile(
        r"^Switch \S+ \S+ Software Version (?P<version>.+)$", re.MULTILINE)
    rx_bootprom = re.compile(
        r"^Bootrom Version is\s+(?P<bootprom>\S+)$", re.MULTILINE)
    rx_hardware = re.compile(
        r"^.*Hardware Version is (?P<hardware>\S+)\s?$", re.MULTILINE)
    rx_platform = re.compile(
        r"^Switch (?P<platform>\S+ \S+) Software Version.*$", re.MULTILINE)
    rx_serial = re.compile(
        r"^.*Product serial number:\s+(?P<serial>\S+)$", re.MULTILINE)

    def execute(self):

        # Fallback to CLI
        plat = self.cli("display version", cached=True)
        version = self.rx_version_3Com.search(plat)
        platform = self.rx_platform.search(plat)
        bootprom = self.rx_bootprom.search(plat)
        hardware = self.rx_hardware.search(plat)

        serial = self.cli("display device manuinfo", cached=True)
        serial = self.rx_serial.search(serial)

        return {
                "vendor": '3Com',
                "platform": platform.group("platform"),
                "version": version.group("version"),
                "attributes": {
                    "Boot PROM": bootprom.group("bootprom"),
                    "HW version": hardware.group("hardware"),
                    "Serial Number": serial.group("serial")
                    }
                }
