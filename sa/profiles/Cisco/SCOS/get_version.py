# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SCOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "Cisco.SCOS.get_version"
    cache = True
    interface = IGetVersion

    rx_version = re.compile(r"^System version: Version (?P<version>[^\n]+)",
        re.MULTILINE | re.DOTALL)
    rx_platform = re.compile(r"((Product ID\s+:\s+)|(Platform:\s+))(?P<platform>\S+)",
        re.MULTILINE | re.DOTALL)
    rx_prod_id = re.compile(r"Product S\/N\s+: (?P<prod_id>\S+)",
        re.MULTILINE | re.DOTALL)
    rx_chass_sn = re.compile(r"SCE8000 Chassis\n(.+\n)serial-num\s+:\s+(?P<chass_sn>\S+)",
        re.MULTILINE | re.DOTALL)
    

    def execute(self):
        v = self.cli("show version", cached=True)
        match = self.rx_version.search(v)
        if match:    
            version = match.group("version")
        match = self.rx_platform.search(v)
        if match:
            platform = match.group("platform")
        match = self.rx_prod_id.search(v)
        r = {
            "vendor": "Cisco",
            "platform": platform,
            "version": version,
            "attributes": {}
            }
        match = self.rx_prod_id.search(v)
        if match:
            r["attributes"].update({"product_id": match.group("prod_id")})
        match = self.rx_chass_sn.search(v)
        if match:
            r["attributes"].update({"chassis_sn": match.group("chass_sn")})
        return r

