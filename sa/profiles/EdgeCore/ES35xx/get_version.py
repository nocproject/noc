# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_sys=re.compile(r"System description:\s+.*?(?P<platform>ES.+?)$",re.MULTILINE|re.DOTALL|re.IGNORECASE)
rx_ver=re.compile(r"Operation code version\s+(?P<version>\S+)",re.MULTILINE|re.DOTALL|re.IGNORECASE)

class Script(noc.sa.script.Script):
    name="EdgeCore.ES35xx.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show system")
        match_sys=rx_sys.search(v)
        v=self.cli("show version")
        match_ver=rx_ver.search(v.replace(":",""))
        sub=match_ver.group("version").split(".")
        if sub[0]=="1":
            platform="ES3526XA-V2"
        elif sub[0]=="2" and sub[1]=="3":
            if int(sub[2])&1==1:
                platform="ES3526XA-38"
            else:
                platform="ES3526XA-1-SL-38"
        return {
            "vendor"    : "EdgeCore",
            "platform"  : platform,
            "version"   : match_ver.group("version"),
        }
