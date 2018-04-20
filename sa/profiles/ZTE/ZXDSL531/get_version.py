# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
<<<<<<< HEAD
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
=======
import noc.sa.script
from noc.sa.interfaces import IGetVersion
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.text import strip_html_tags
import re

rx_html_ver = re.compile(r"Firmware Version\s+\S+\s+(?P<version>\S+)")

<<<<<<< HEAD

class Script(BaseScript):
    name = "ZTE.ZXDSL531.get_version"
    cache = True
    interface = IGetVersion

=======

class Script(noc.sa.script.Script):
    name = "ZTE.ZXDSL531.get_version"
    cache = True
    implements = [IGetVersion]

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute(self):
        if self.access_profile.scheme == self.TELNET:
            v = self.cli("swversion show")
            platform, version = v.split()
        elif self.access_profile.scheme == self.HTTP:
            v = self.http.get("/info.html")
            v = strip_html_tags(v)
            match = rx_html_ver.search(v)
            version = match.group("version")
        else:
            raise Exception("Unsupported access scheme")
        return {
            "vendor": "ZTE",
            "platform": "ZXDSL531",
            "version": version
        }
