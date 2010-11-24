# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3xxx.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig

class Script(NOCScript):
    name="DLink.DGS3xxx.get_config"
    implements=[IGetConfig]
    ##
    ## DGS-3612, DGS-3612G, DGS-3627, DGS-3627G, DGS-3650
    ##
    @NOCScript.match(platform__regex=r"(3612|3627|3650)")
    def execute_config_active(self):
        config=self.cli("show config active")
        config=self.strip_first_lines(config,1)
        return self.cleaned_config(config)
    
    ##
    ## DGS-3100-24, DGS-3100-24P, DGS-3100-24TG, DGS-3100-49, DGS-3100-48P
    ##
    @NOCScript.match(platform__contains="3100")
    def execute_configuration_running(self):
        return self.cleaned_config(self.cli("show configuration running"))
    
    ##
    ## DGS-3024, DGS-3048
    ##
    @NOCScript.match(platform__regex=r"(3024|3048)")
    def execute_not_supported(self):
        raise self.NotSupportedError()
    
    ##
    ## Other
    ##
    @NOCScript.match()
    def execute_config_current_config(self):
        return self.cleaned_config(self.cli("show config current_config"))
    
