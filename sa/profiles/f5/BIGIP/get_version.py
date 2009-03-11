# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
import re

rx_ver=re.compile("BIG-IP Version (?P<version>.+?)$",re.MULTILINE)

class Script(noc.sa.script.Script):
    name="f5.BIGIP.get_version"
    implements=[IGetVersion]
    def execute(self):
        v=self.cli("version")
        match=rx_ver.search(v)
        return {
            "vendor"    : "f5",
            "platform"  : "BIG-IP",
            "version"   : match.group("version"),
        }
