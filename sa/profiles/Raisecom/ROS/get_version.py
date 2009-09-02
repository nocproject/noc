# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Raisecom.ROS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile(r"^Product name:\s+(?P<platform>\S+).*ROS  Version ROS_(?P<version>.+?)\.\(Compiled",re.MULTILINE|re.DOTALL)

class Script(noc.sa.script.Script):
    name="Raisecom.ROS.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("show version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "Raisecom",
            "platform"  : match.group("platform"),
            "version"   : match.group("version"),
        }
