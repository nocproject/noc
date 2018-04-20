# -*- coding: utf-8 -*-
__author__ = 'FeNikS'
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Tangram.GT21.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
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
=======
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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVersion


class Script(NOCScript):
    name = "Tangram.GT21.get_version"
    cache = True
    implements = [IGetVersion]     
    
    def execute(self):
        #todo
        platform = "_p01" 
        version = "_v01"                                  
        
        return {
            "vendor": "Tangram",
            "platform": platform ,
            "version": version 
        }
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
