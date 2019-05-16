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


class Script(BaseScript):
    name = "DLink.DxS.get_config"
    interface = IGetConfig

    def execute_cli(self, policy="r"):
        assert policy in ("r", "s")

        # DGS-3612, DGS-3612G, DGS-3627, DGS-3627G, DGS-3650
        if self.is_dgs3600 or self.is_dgs3400:
            if policy == "s":
                config = self.cli("show config boot_up")
            else:
                config = self.cli("show config active")
            config = self.strip_first_lines(config, 1)
            return self.cleaned_config(config)
        # DES-1210-10/ME, DES-1210-26/ME, DES-1210-28/ME, DES-1210-52/ME
        # DGS-1210-10/ME, DGS-1210-12/ME, DGS-1210-28/ME, DGS-1210-52/ME
        # DGS-1100-06/ME, DGS-1100-10/ME
        # DES-3526, DES-3550
        elif self.is_des1210 or self.is_dgs1210 or self.is_dgs1100 or self.is_des30xx or self.is_des3500:
            if policy == "s":
                config = self.cli("show config config_in_nvram")
            else:
                config = self.cli("show config current_config")
            if self.is_des1210 or self.is_dgs1210 or self.is_dgs1100_06:
                config = self.strip_first_lines(config, 4)
            else:
                config = self.strip_first_lines(config, 2)
            config = re.sub(r"config time \d+[^\n]*\n", "", config)
            while config.endswith("\n\n"):
                config = config[:-1]
            return self.cleaned_config(config)
        # DGS-3024, DGS-3048
        # DES-3226, DES-3226L, DES-3226S, DES-3250TG
        # DES-3326, DES-3326S, DES-3326SR, DES-3350SR, DES-3350TG, DES-3352SR
        elif self.is_dgs30xx or self.is_des3x2x:
            raise self.NotSupportedError()
        else:
            try:
                if policy == "s":
                    config = self.cli("show config boot_up")
                else:
                    config = self.cli("show config current_config")
            except self.CLISyntaxError:
                raise self.NotSupportedError()
            config = self.strip_first_lines(config, 1)
            return self.cleaned_config(config)
