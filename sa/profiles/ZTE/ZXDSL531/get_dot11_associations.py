# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetdot11associations import IGetDot11Associations
from noc.lib.text import strip_html_tags
import re

rx_mac = re.compile("(?P<mac>[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2})")


class Script(BaseScript):
    name = "ZTE.ZXDSL531.get_dot11_associations"
    interface = IGetDot11Associations

    def execute(self):
        if self.access_profile.scheme == self.TELNET:
            v = self.cli("wlctl authe_sta_list")
        elif self.access_profile.scheme == self.HTTP:
            v = self.http.get("/wlclientview.cmd")
            v = strip_html_tags(v)
        else:
            raise Exception("Unsupported access scheme")
        r = []
        for l in v.split("\n"):
            m = rx_mac.search(l)
            if m:
                r.append({"mac": m.group("mac")})
        return r
