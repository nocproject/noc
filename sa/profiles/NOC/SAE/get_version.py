# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NOC.SAE.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetVersion
from noc.lib.version import get_version

class Script(noc.sa.script.Script):
    name="NOC.SAE.get_version"
    cache=True
    implements=[IGetVersion]
    def execute(self):
        return {
            "vendor"    : "NOC",
            "platform"  : "NOC",
            "version"   : get_version()
        }
