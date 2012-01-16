# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linksys.VoIP.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetVersion
from noc.lib.text import strip_html_tags


class Script(noc.sa.script.Script):
    name = "Linksys.VoIP.get_version"
    cache = True
    implements = [IGetVersion]

    rx_platform = re.compile(
        r"^Product Name:+(?P<platform>\S+)+Serial Number:+(?P<serial>\S+)$",
        re.MULTILINE)
    rx_version = re.compile(
        r"^Software Version:+(?P<version>\S+)+Hardware Version:+(?P<hardware>\S+)$",
        re.MULTILINE)

    def execute(self):
        v = self.http.get("/")
        v = strip_html_tags(v)
        platform = self.rx_platform.search(v)
        version = self.rx_version.search(v)
        return {
                "vendor": "Linksys",
                "platform": platform.group("platform"),
                "version": version.group("version"),
                "attributes": {
                            "HW version": version.group("hardware"),
                            "Serial Number": platform.group("serial"),
                            }
                }
