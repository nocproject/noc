# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rotek.BT.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from tornado.iostream import StreamClosedError

class Script(BaseScript):
    name = "Rotek.BT.get_version"
    cache = True
    interface = IGetVersion
    reuse_cli_session = False
    keep_cli_session = False

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                oid = self.snmp.get("1.3.6.1.2.1.1.1.0",
                                        cached=True)
                v = oid.split(",")[1].strip().split(".")
                platform = oid.split(",")[0].strip()
                version = "%s.%s" % (v[0], v[1])

                result = {
                    "vendor": "Rotek",
                    "version": version,
                    "platform": platform,
                    #"attributes": {
                        #"HW version": hwversion}
                }
                return result
            except self.snmp.TimeOutError:
                pass
        return result