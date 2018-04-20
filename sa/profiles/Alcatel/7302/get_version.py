# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.7302.get_version
# Author: scanbox@gmail.com
# ----------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
import re


class Script(BaseScript):
    name = "Alcatel.7302.get_version"
    cache = True
    interface = IGetVersion

    rx_sys = re.compile(
        r"actual-type\s*?:\s*(?P<platform>.+?)\s*$", re.MULTILINE)
    rx_ver = re.compile(
        r".+?\/*(?P<version>[A-Za-z0-9.]+?)\s+\S+\s+active.*$", re.MULTILINE)

    def execute(self):
        self.cli("environment inhibit-alarms mode batch", ignore_errors=True)
        try:
            v = self.cli("show equipment isam")
        except self.CLISyntaxError:
            v = self.cli("show equipment gebc")
        match_sys = self.rx_sys.search(v)
        v = self.cli("show software-mngt oswp")
        match_ver = self.rx_ver.search(v)
=======
##----------------------------------------------------------------------
## Alcatel.7302.get_version
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

rx_sys = re.compile(r"actual-type\s*?:\s*(?P<platform>.+?)\s*$",
    re.MULTILINE | re.DOTALL)
rx_ver = re.compile(r".+?\/*(?P<version>[A-Za-z0-9.]+?)\s+\S+\s+active.*$",
    re.MULTILINE | re.DOTALL)

class Script(noc.sa.script.Script):
    name = "Alcatel.7302.get_version"
    cache = True
    implements = [IGetVersion]

    def execute(self):
        self.cli("environment inhibit-alarms mode batch")
        v = self.cli("show equipment isam")
        match_sys = rx_sys.search(v)
        v = self.cli("show software-mngt oswp")
        match_ver = rx_ver.search(v)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return {
            "vendor": "Alcatel",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version")
        }
