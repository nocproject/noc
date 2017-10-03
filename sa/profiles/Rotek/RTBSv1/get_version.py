# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rotek.RTBSv1.get_version
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
    name = "Rotek.RTBSv1.get_version"
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
                v = oid.split(" ")[2].strip().split(".")
                platform = "%s.%s" % (oid.split(" ")[0].strip(), oid.split(" ")[1].strip())
                version = "%s.%s" % (v[0], v[1])

                result = {
                    "vendor": "Rotek",
                    "version": version,
                    "platform": platform,
                    # "attributes": {
                    # "HW version": hwversion}
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
        sw = "%s.%s" % (sres[0], sres[1])
        result = {
            "vendor": "Rotek",
            "version": sw,
            "attributes": {
                "HW version": hwversion}
        }
        with self.profile.shell(self):
                v = self.cli("cat /etc/product", cached=True)
                for line in v.splitlines():
                    l = line.split(":", 1)
                    if "productName" in l[0]:
                        platform = l[1].strip().replace(" ",".").replace("\"","").replace(",","")
                        result["platform"] = platform
        return result
