# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ubiquiti.AirOS.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_version=re.compile("\.v(?P<version>[^@]+)@")

class Script(noc.sa.script.Script):
    name="Ubiquiti.AirOS.get_version"
    implements=[IGetVersion]
    def execute(self):
        ps1=self.cli("echo $PS1|sed 's/#/@/'") # Replace # with @ to prevent prompt matching
        v_match=rx_version.search(ps1)
        board=self.cli("grep board.name /etc/board.info")
        l,r=board.split("=")
        board=r.strip()
        return {
            "vendor"   : "Ubiquiti",
            "platform" : board,
            "version"  : v_match.group("version"),
        }