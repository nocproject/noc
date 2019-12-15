# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.ISW.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Extreme.ISW.get_version"
    cache = True
    interface = IGetVersion

    rx_platform = re.compile(r"^Product\s+:\s+(?P<platform>.+),.+", re.MULTILINE)
    rx_version = re.compile(r"^Software Version\s+:\s+(?P<version>\S+)", re.MULTILINE)
    rx_image = re.compile(r"Image\s+:\s+(?P<image>\S+)\s\(primary\)", re.MULTILINE)
    rx_active_slot = re.compile(r"^\*\S+\s[\d-]+\s(?P<slot_num>[\d-]).*$", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        platform = self.rx_platform.search(v).group("platform")
        version = self.rx_version.search(v).group("version")
        image = self.rx_image.search(v).group("image")
        return {"vendor": "Extreme", "platform": platform, "version": version, "image": image}
