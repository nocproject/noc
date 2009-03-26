# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
from noc.lib.text import strip_html_tags
import re

rx_html_ver=re.compile(r"Firmware Version\s+\S+\s+(?P<version>\S+)")

class Script(noc.sa.script.Script):
    name="ZTE.ZXDSL531.get_version"
    implements=[IGetVersion]
    def execute(self):
        if self.access_profile.scheme==self.TELNET:
            v=self.cli("swversion show")
            platform,version=v.split()
        elif self.access_profile.scheme==self.HTTP:
            v=self.http.get("/info.html")
            v=strip_html_tags(v)
            match=rx_html_ver.search(v)
            version=match.group("version")
        else:
            raise Exception("Unsupported access scheme")
        return {
            "vendor"    : "ZTE",
            "platform"  : "ZXDSL531",
            "version"   : version,
        }
