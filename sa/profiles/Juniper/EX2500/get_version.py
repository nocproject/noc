# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Juniper.EX2500.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Juniper.EX2500.get_version"
    interface = IGetVersion
    cache = True

    rx_platform = re.compile(
        r"Juniper Networks (?P<platform>\S+) .+ Switch"
    )
    rx_version = re.compile(
        r"Software Version (?P<version>\S+), Boot Version (?P<bootprom>\S+),"
    )
    rx_serial = re.compile(r"Serial Number:\s+(?P<serial>\S+)")
    rx_hardware = re.compile(r"Hardware Revision:\s+(?P<hardware>\S+)")

    def execute(self):
        v = self.cli("show sys-info", cached=True)
        match = self.rx_platform.search(v)
        platform = match.group("platform")
        match = self.rx_version.search(v)
        r = {
            "vendor": "Juniper",
            "platform": platform,
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootprom"),
            }
        }
        match = self.rx_serial.search(v)
        if match:
            r["attributes"]["Serial Number"] = match.group("serial")
        match = self.rx_hardware.search(v)
        if match:
            r["attributes"]["HW version"] = match.group("hardware")
        return r
