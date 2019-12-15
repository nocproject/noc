# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DxS.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig
from noc.sa.profiles.DLink.DxS.profile import DGS3600


class Script(BaseScript):
    name = "DLink.DxS.get_config"
    interface = IGetConfig

    # DGS-3612, DGS-3612G, DGS-3627, DGS-3627G, DGS-3650
    @BaseScript.match(DGS3600)
    def execute_config_active(self, **kwargs):
        config = self.cli("show config active")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)

    # DGS-3024, DGS-3048
    @BaseScript.match(platform__regex=r"DGS-(3024|3048)")
    def execute_config_current30(self, **kwargs):
        config = self.cli("show config current_config")
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)

    # DES-1210-28/ME/B2, DES-1210-26/ME, DES-1210-10/ME
    @BaseScript.match(platform__regex=r"DES-1210-(10|26|28)\/ME")
    def execute_config_current12(self, **kwargs):
        config = self.cli("show config current_config")
        config = self.strip_first_lines(config, 4)
        config = re.sub(r"config time \d+[^\n]*\n", "", config)
        while config.endswith("\n\n"):
            config = config[:-1]
        return self.cleaned_config(config)

    # DES-1210-28, DES-1210-52
    @BaseScript.match(platform__regex=r"DES-1210")
    def execute_not_supported12(self, **kwargs):
        raise self.NotSupportedError()

    # DES-3226, DES-3226L, DES-3226S, DES-3250TG
    @BaseScript.match(platform__regex=r"DES-32(26|50)")
    def execute_not_supported32(self, **kwargs):
        raise self.NotSupportedError()

    # DES-3326, DES-3326S, DES-3326SR, DES-3350SR, DES-3350TG, DES-3352SR
    @BaseScript.match(platform__regex=r"DES-33(26|50|52)")
    def execute_not_supported33(self, **kwargs):
        raise self.NotSupportedError()

    # DGS-1100-06/ME
    @BaseScript.match(platform__regex=r"DGS-1100-06\/ME")
    def execute_config_current11(self, **kwargs):
        config = self.cli("show config current_config")
        config = self.strip_first_lines(config, 4)
        config = re.sub(r"config time \d+[^\n]*\n", "", config)
        while config.endswith("\n\n"):
            config = config[:-1]
        return self.cleaned_config(config)

    # Other
    @BaseScript.match()
    def execute_config_current_config(self, **kwargs):
        try:
            config = self.cli("show config current_config")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
