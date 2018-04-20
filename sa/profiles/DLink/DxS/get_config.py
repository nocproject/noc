# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DxS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig
from noc.sa.profiles.DLink.DxS import DGS3600


class Script(BaseScript):
    name = "DLink.DxS.get_config"
    interface = IGetConfig
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

    ##
    ## DGS-3612, DGS-3612G, DGS-3627, DGS-3627G, DGS-3650
    ##
<<<<<<< HEAD
    @BaseScript.match(DGS3600)
=======
    @NOCScript.match(DGS3600)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute_config_active(self):
        config = self.cli("show config active")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)

    ##
    ## DGS-3024, DGS-3048
    ##
<<<<<<< HEAD
    @BaseScript.match(platform__regex=r"DGS-(3024|3048)")
=======
    @NOCScript.match(platform__regex=r"DGS-(3024|3048)")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute_config_current(self):
        config = self.cli("show config current_config")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)

    ##
<<<<<<< HEAD
    ## DES-1210-28/ME/B2, DES-1210-26/ME, DES-1210-10/ME
    ##
    @BaseScript.match(platform__regex=r"DES-1210-(10|26|28)\/ME")
    def execute_config_current(self):
        config = self.cli("show config current_config")
        config = self.strip_first_lines(config, 4)
        config = re.sub("config time \d+[^\n]*\n", "", config)
        while config.endswith("\n\n"):
            config = config[:-1]
=======
    ## DES-1210-28/ME/B2
    ##
    @NOCScript.match(platform__regex=r"DES-1210-28\/ME")
    def execute_config_current(self):
        config = self.cli("show config current_config")
        config = self.strip_first_lines(config, 3)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return self.cleaned_config(config)

    ##
    ## DES-1210-28, DES-1210-52
    ##
<<<<<<< HEAD
    @BaseScript.match(platform__regex=r"DES-1210")
=======
    @NOCScript.match(platform__regex=r"DES-1210")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute_not_supported(self):
        raise self.NotSupportedError()

    ##
    ## DES-3226, DES-3226L, DES-3226S, DES-3250TG
    ##
<<<<<<< HEAD
    @BaseScript.match(platform__regex=r"DES-32(26|50)")
=======
    @NOCScript.match(platform__regex=r"DES-32(26|50)")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute_not_supported(self):
        raise self.NotSupportedError()

    ##
    ## DES-3326, DES-3326S, DES-3326SR, DES-3350SR, DES-3350TG, DES-3352SR
    ##
<<<<<<< HEAD
    @BaseScript.match(platform__regex=r"DES-33(26|50|52)")
=======
    @NOCScript.match(platform__regex=r"DES-33(26|50|52)")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute_not_supported(self):
        raise self.NotSupportedError()

    ##
<<<<<<< HEAD
    ## DGS-1100-06/ME
    ##
    @BaseScript.match(platform__regex=r"DGS-1100-06\/ME")
    def execute_config_current(self):
        config = self.cli("show config current_config")
        config = self.strip_first_lines(config, 4)
        config = re.sub("config time \d+[^\n]*\n", "", config)
        while config.endswith("\n\n"):
            config = config[:-1]
        return self.cleaned_config(config)

    ## Other
    ##
    @BaseScript.match()
    def execute_config_current_config(self):
        try:
            config = self.cli("show config current_config")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
=======
    ## Other
    ##
    @NOCScript.match()
    def execute_config_current_config(self):
        config = self.cli("show config current_config")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
