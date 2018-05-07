# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ericsson.BS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Ericsson.BS.get_version"
    interface = IGetVersion

    rx_sn = re.compile("serial number:\s+(?P<serial>\S+)\).", re.MULTILINE)

    def execute(self):
        v = self.cli("csti info")
        match = self.rx_sn.search(v)
        if match:
            serial = match.group("serial")
        else:
            serial = "None"
        r = {
            "vendor": "Ericsson",
            "platform": "eNodeB",
            "version": "None",
            "attributes": {
                "Serial Number": serial
            }
        }
        return r
