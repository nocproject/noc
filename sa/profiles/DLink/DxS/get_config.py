# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_config
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetConfig
from noc.sa.profiles.DLink.DxS import DGS3600


class Script(NOCScript):
    name = "DLink.DxS.get_config"
    implements = [IGetConfig]
    TIMEOUT = 360

    ##
    ## DGS-3612, DGS-3612G, DGS-3627, DGS-3627G, DGS-3650
    ##
    @NOCScript.match(DGS3600)
    def execute_config_active(self):
        config = self.cli("show config active")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)

    ##
    ## DGS-3024, DGS-3048
    ##
    @NOCScript.match(platform__regex=r"DGS-(3024|3048)")
    def execute_config_current(self):
        config = self.cli("show config current_config")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)

    ##
    ## DES-1210-28/ME/B2
    ##
    @NOCScript.match(platform__regex=r"DES-1210-28\/ME")
    def execute_config_current(self):
        config = self.cli("show config current_config")
        config = self.strip_first_lines(config, 31)
        return self.cleaned_config(config)

    ##
    ## DES-1210-28, DES-1210-52
    ##
    @NOCScript.match(platform__regex=r"DES-1210")
    def execute_not_supported(self):
        raise self.NotSupportedError()

    ##
    ## DES-3226, DES-3226L, DES-3226S, DES-3250TG
    ##
    @NOCScript.match(platform__regex=r"DES-32(26|50)")
    def execute_not_supported(self):
        raise self.NotSupportedError()

    ##
    ## DES-3326, DES-3326S, DES-3326SR, DES-3350SR, DES-3350TG, DES-3352SR
    ##
    @NOCScript.match(platform__regex=r"DES-33(26|50|52)")
    def execute_not_supported(self):
        raise self.NotSupportedError()

    ##
    ## Other
    ##
    @NOCScript.match()
    def execute_config_current_config(self):
        config = self.cli("show config current_config")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
