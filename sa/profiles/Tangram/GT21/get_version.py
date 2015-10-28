# -*- coding: utf-8 -*-
__author__ = 'FeNikS'
##----------------------------------------------------------------------
## Tangram.GT21.get_version
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
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
    name = "Tangram.GT21.get_version"
    cache = True
    interface = IGetVersion
    
    def execute(self):
        platform = "GT21"
        version = "Unknown"
        
        return {
            "vendor": "Tangram",
            "platform": platform,
            "version": version 
        }
