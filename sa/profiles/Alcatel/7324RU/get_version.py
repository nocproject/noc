# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.7324RU.get_config
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "Alcatel.7324RU.get_version"
    cache = True
    interface = IGetVersion

    rx_sys = re.compile(r"Model\s*:\s*(?P<platform>.+?)\s*$",
        re.MULTILINE | re.DOTALL)
    rx_ver = re.compile(r".+?version\s*:\s*(?P<version>.+?)\s+\|.*$",
        re.MULTILINE | re.DOTALL)
    rx_boot_ver = re.compile(r"Bootbase version: (?P<bootprom>\S+)")
    rx_hw_ver = re.compile(r"Hardware version: (?P<hw_version>\S+)")
    rx_serial = re.compile(r"Serial number: (?P<serial>\S+)")

    def execute(self):
        v = self.cli("sys info show", cached=True)
        match_sys = self.rx_sys.search(v)
        match_ver = self.rx_ver.search(v)
        r = {
            "vendor": "Alcatel",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version"),
            "attributes": {}
        }
        match = self.rx_boot_ver.search(v)
        if match:
            r["attributes"]["Boot PROM"] = match.group("bootprom")
        match = self.rx_hw_ver.search(v)
        if match:
            r["attributes"]["HW version"] = match.group("hw_version")
        match = self.rx_serial.search(v)
        if match:
            r["attributes"]["Serial Number"] = match.group("serial")
        return r
=======
##----------------------------------------------------------------------
## Alcatel.7324RU.get_config
## Author: scanbox@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_sys = re.compile(r"Model\s*:\s*(?P<platform>.+?)\s*$",
    re.MULTILINE | re.DOTALL)
rx_ver = re.compile(r".+?version\s*:\s*(?P<version>.+?)\s+\|.*$",
    re.MULTILINE | re.DOTALL)

class Script(noc.sa.script.Script):
    name = "Alcatel.7324RU.get_version"
    cache = True
    implements = [IGetVersion]

    def execute(self):
        v = self.cli("sys info show")
        match_sys = rx_sys.search(v)
        match_ver = rx_ver.search(v)
        return {
            "vendor": "Alcatel",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version")
        }
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
