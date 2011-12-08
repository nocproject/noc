# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion
from noc.lib.text import strip_html_tags


class Script(NOCScript):
    name = "Audiocodes.Mediant2000.get_version"
    cache = True
    implements = [IGetVersion]

    rx_ver = re.compile(
        r"^Board type: (?P<platform>.+), firmware version (?P<version>\S+)",
        re.MULTILINE | re.DOTALL)
    rx_html_ver = re.compile(r"Version ID:\s+(?P<version>\S+)",
                             re.MULTILINE | re.DOTALL)

    def execute(self):
        if self.access_profile.scheme in [self.TELNET, self.SSH]:
            v = self.cli("show info")
            match = self.rx_ver.search(v)
            return {
                "vendor": "Audiocodes",
                "platform": match.group("platform"),
                "version": match.group("version"),
                }
        elif self.access_profile.scheme == self.HTTP:
            v = self.http.get("/SoftwareVersion")
            v = strip_html_tags(v)
            match = self.rx_html_ver.search(v)
            return {
                "vendor": "Audiocodes",
                "platform": "Mediant2000",
                "version": match.group("version"),
                }
        else:
            raise Exception("Unsupported access scheme")
