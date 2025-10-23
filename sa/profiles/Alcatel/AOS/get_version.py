# ----------------------------------------------------------------------
# Alcatel.AOS.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Alcatel.AOS.get_version"
    cache = True
    interface = IGetVersion

    rx_sys = re.compile(
        r"Module in slot.+?Model.*?Name:\s+(?P<platform>.+?),$", re.MULTILINE | re.DOTALL
    )
    rx_ver = re.compile(r"System.*?Description:\s+(?P<version>.+?)\s.*$", re.MULTILINE | re.DOTALL)
    rx_ser = re.compile(r"Serial Number:\s+(?P<serial>.+?),$", re.MULTILINE | re.DOTALL)
    rx_ver1 = re.compile(
        r"System.*?Description:\s+Alcatel-Lucent\s+(?P<ver1>\S+)\s+(?P<version>\S+)\s.*$",
        re.MULTILINE | re.DOTALL,
    )

    def execute(self):
        v = self.cli("show ni")
        match_sys = self.rx_sys.search(v)
        match_serial = self.rx_ser.search(v)
        v = self.cli("show system")
        match = self.rx_ver.search(v)
        version = match.group("version")
        if version == "Alcatel-Lucent":
            match = self.rx_ver1.search(v)
            version = match.group("version")
            if version.endswith(","):
                version = match.group("ver1")
        return {
            "vendor": "Alcatel",
            "platform": match_sys.group("platform"),
            "version": version,
            "attributes": {"Serial Number": match_serial.group("serial")},
        }
