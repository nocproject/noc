# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.lib.text import strip_html_tags


class Script(BaseScript):
    name = "TFortis.PSW.get_version"
    cache = True
    interface = IGetVersion

    rx_html_ver = re.compile(
        r"Firmware version(?P<version>.*)Bootloader version(?P<bootloader>.*)\sMAC")
    rx_html_platform = re.compile(r"^TFortis (?P<platform>.*)\x00")

    def execute(self):
        v = self.http.get("/header_name.shtml", eof_mark="</html>")
        v = strip_html_tags(v)
        platform = self.rx_html_platform.search(v)
        v = self.http.get("/main.shtml", eof_mark="</html>")
        v = strip_html_tags(v)
        match = self.rx_html_ver.search(v)
        return {
            "vendor": "TFortis",
            "platform": platform.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Bootloader": match.group("bootloader"),
            }
        }
