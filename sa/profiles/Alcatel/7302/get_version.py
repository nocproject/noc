# -*- coding: utf-8 -*-
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
        return {
            "vendor": "Alcatel",
            "platform": match_sys.group("platform"),
            "version": match_ver.group("version")
        }
