# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## H3C.VRP.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion



class Script(NOCScript):
    name = "H3C.VRP.get_version"
    cache = True
    implements = [IGetVersion]


    rx_ver = re.compile(r"^.*?Switch\s(?P<platform>.+?)\sSoftware\s\Version"
        r"\s3Com\sOS\sV(?P<version>.+?)$",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_ver1 = re.compile(r"^Comware\sSoftware,\s\Version\s(?P<version>.+?),.+"
        r"^H3C (?P<platform>\S+) uptime is",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)
    rx_hw = re.compile(r"Hardware Version is (?P<hardware>\S+)")
    rx_boot = re.compile(r"Bootrom Version is (?P<bootprom>\S+)")

    def execute(self):
        v = self.cli("display version")
        match = self.rx_ver.search(v)
        if not match:
            match = self.rx_ver1.search(v)
        r = {
            "vendor": "H3C",
            "platform": match.group("platform"),
            "version": match.group("version")
        }
        hw = self.rx_hw.search(v)
        boot = self.rx_boot.search(v)
        if hw or boot:
            r.update({"attributes": {}})
            if hw:
                r["attributes"].update({"HW version": hw.group("hardware")})
            if boot:
                r["attributes"].update({"Boot PROM": boot.group("bootprom")})
        return r
