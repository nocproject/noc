# ---------------------------------------------------------------------
# Angtel.Topaz.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Angtel.Topaz.get_version"
    cache = True
    interface = IGetVersion

    rx_port = re.compile(
        r"^(?P<port>(?:Fa|Gi|Te|Po)\S+)\s+(?P<type>\S+)\s+\S+\s+\S+\s+\S+\s+\S+\s+(?:Up|Down|Not Present)",
        re.MULTILINE | re.IGNORECASE,
    )
    rx_ver = re.compile(
        r"^\s*SW version\s+(?P<version>\S+).*\n"
        r"^\s*Boot version\s+(?P<bootprom>\S+).*\n"
        r"^\s*HW version\s*(?P<hardware>\S+)?.*\n",
        re.MULTILINE,
    )
    rx_serial = re.compile(r"^\s*Serial number :\s*(?P<serial>\S+)?")

    PLATFORM = {
        (0, 2, 8): "2O-8E",
        (0, 4, 8): "4O-8E",
        (0, 2, 16): "2O-16E",
        (0, 2, 24): "2O-24E",
        (2, 0, 8): "2X-8E",
    }

    def execute_cli(self):
        o = 0
        E = 0
        X = 0
        v = self.cli("show interfaces status", cached=True)
        for match in self.rx_port.finditer(v):
            if match.group("type") in ["100M-Copper", "1G-Copper"]:
                E += 1
            elif match.group("type") in ["1G-Combo-C", "1G-Combo-F"]:
                o += 1
            elif match.group("type") in ["10G-Combo-C", "10G-Combo-F"]:
                X += 1
        platform = self.PLATFORM.get((X, o, E))
        if not platform:
            platform = "Unknown"
        # if platform in ["2o-8E", "2o-16E", "2o-24E"]:
        #    try:
        #        v = self.cli("show hw info", cached=True)
        #        if "Session meter (KW*H) =" in v:
        #            platform = "%s max" % platform
        #        else:
        #            platform = "%s optim" % platform
        #    except self.CLISyntaxError:
        #        pass
        v = self.cli("show version", cached=True)
        match = self.rx_ver.search(v)
        r = {
            "vendor": "Angtel",
            "platform": "Topaz-%s" % platform,
            "version": match.group("version"),
            "attributes": {"Boot PROM": match.group("bootprom")},
        }
        if match.group("hardware"):
            r["attributes"]["HW version"] = match.group("hardware")
        v = self.cli("show system id", cached=True)
        match = self.re_search(self.rx_serial, v)
        if match.group("serial"):
            r["attributes"]["Serial Number"] = match.group("serial")
        return r
