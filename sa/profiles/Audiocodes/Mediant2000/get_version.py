# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.text import strip_html_tags


class Script(BaseScript):
    name = "Audiocodes.Mediant2000.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r"^Board type: (?P<platform>.+), firmware version (?P<version>\S+)",
        re.MULTILINE | re.DOTALL,
    )
    rx_html_ver = re.compile(r"Version ID:\s+(?P<version>\S+)", re.MULTILINE | re.DOTALL)

    def execute(self):
        if "http_protocol" in self.credentials:
            return self.execute_http()
        return self.execute_cli()

    def execute_cli(self):
        v = self.cli("show info")
        match = self.rx_ver.search(v)
        return {
            "vendor": "Audiocodes",
            "platform": match.group("platform"),
            "version": match.group("version"),
        }

    def execute_http(self):
        v = self.http.get("/SoftwareVersion")
        v = strip_html_tags(v)
        match = self.rx_html_ver.search(v)
        return {
            "vendor": "Audiocodes",
            "platform": "Mediant2000",
            "version": match.group("version"),
        }
