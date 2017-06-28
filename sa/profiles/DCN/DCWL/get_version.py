# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: DCN
# OS:     DCWL
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
'''
'''
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "DCN.DCWL.get_version"
    cache = True
    interface = IGetVersion
    
    def execute(self):
        r = []
        c = self.cli("get device-info", cached=True)
        for line in c.splitlines():
            r = line.split(' ', 1)
            if r[0] == "device-name":
                platform = r[1].strip()
            if r[0] == "version-id":
                version = r[1].strip()
        d = self.cli("get system detail", cached=True)  
        for line in d.splitlines():     
            r = line.split(' ', 1)
            if r[0] == "version":
                hwversion = r[1].strip()
            if r[0] == "serial-number":
                sn = r[1].strip()   
        return {
            "vendor": "DCN",
            "platform": platform,
            "version": version,
            "attributes": {
                "HW version": hwversion,
                "Serial Number": sn
                          }
            }
