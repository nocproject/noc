# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Nateks.flexgain.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):

    name = "Nateks.netxpert.get_version"
    cache = True
    interface = IGetVersion

    rx_ver = re.compile(
        r".*Series Software, Version (?P<version>[^ ,]+)\, RELEASE SOFTWARE\n"
        r".*ROM: System Bootstrap, Version (?P<bootrom>[^ ,]+)\n"
        r"^Serial num:(?P<sn>[^ ,]+),.*\n"
        r"Nateks (?P<platform>[^ ,]+) RISC\n"
        , re.MULTILINE | re.DOTALL | re.IGNORECASE)
    
    def execute(self):
        v = ""
        v = self.cli("show version ", cached=True)
    	
        match = self.re_search(self.rx_ver, v)
        
        return {
            "vendor": "Nateks",
            "platform": match.group("platform"),
            "version": match.group("version"),
            "attributes": {
                "Boot PROM": match.group("bootrom"),
                "SN": match.group("sn"),
                }
            
            }

