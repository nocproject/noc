# ----------------------------------------------------------------------
# BDCOM.IOS.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "BDCOM.IOS.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"product_ID\s*:\s*(?P<platform>\d+)")
    rx_version = re.compile(r"Software, Version (?P<version>\S+ Build \d+)")
    rx_bootprom = re.compile(r"ROM: System Bootstrap, Version (?P<bootprom>\S+),")
    rx_serial = re.compile(r"Serial num\s*:\s*(?P<serial>\S+)")
    rx_hardware = re.compile(r"hardware version\s*:\s*(?P<hardware>\S+)")

    platforms = {
        "347": "S2210PB",
        "455": "S3900-48M6X",
        "458": "S2928EF",
    }

    def execute(self):
        c = self.cli("show version", cached=True)
        match = self.rx_platform.search(c)
        platform = self.platforms[match.group("platform")]
        match = self.rx_version.search(c)
        version = match.group("version")
        match = self.rx_bootprom.search(c)
        bootprom = match.group("bootprom")
        match = self.rx_serial.search(c)
        serial = match.group("serial")
        serial = serial.strip(",")
        match = self.rx_hardware.search(c)
        hardware = match.group("hardware")
        return {
            "vendor": "BDCOM",
            "platform": platform,
            "version": version,
            "attributes": {"Boot PROM": bootprom, "HW version": hardware, "Serial Number": serial},
        }
