# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rotek.RTBS.get_version
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
    name = "Rotek.RTBS.get_version"
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

        # Fallback to CLI
        try:
            c = self.cli("show software version")
        except self.CLISyntaxError:
            c = self.cli("show software-version")
        line = c.split(":")
        res = line[1].strip().split(".", 2)
        hwversion = "%s.%s" % (res[0], res[1])
        sres = res[2].split(".")
        version = "%s.%s" % (sres[0], sres[1])
        result = {
            "vendor": "Rotek",
            "version": version,
            "attributes": {
                "HW version": hwversion}
        }
        with self.profile.shell(self):
                v = self.cli("cat /etc/product", cached=True)
                for line in v.splitlines():
                    l = line.split(" = ", 1)
                    if "product.id" in l[0]:
                        platform = l[1].strip()
                        result["platform"] = platform
        return result