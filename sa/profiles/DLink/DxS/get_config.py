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

    rx_des = re.compile(r"Device Type\s+:\s*(?P<platform>\S+)")
    rx_dgs36xx = re.compile(r"DGS-36(?:12|12G|27|27G|50)")
    rx_dgs30xx = re.compile(r"DGS-(3024|3048)")
    rx_des1210me = re.compile(r"DES-1210-(10|26|28)\/ME")
    rx_dgs1100_06me = re.compile(r"DGS-1100-06\/ME")
    rx_not_supported1 = re.compile(r"DES-1210")
    rx_not_supported2 = re.compile(r"DES-32(26|50)")
    rx_not_supported3 = re.compile(r"DES-33(26|50|52)")

    def execute_cli(self, policy="r"):
        assert policy in ("r", "s")

        platform = self.scripts.get_version()["platform"]

        # DGS-3612, DGS-3612G, DGS-3627, DGS-3627G, DGS-3650
        if self.rx_dgs36xx.search(platform):
            if policy == "s":
                config = self.cli("show config boot_up")
            else:
                config = self.cli("show config active")
            config = self.strip_first_lines(config, 1)
            return self.cleaned_config(config)

        # DGS-3024, DGS-3048
        if self.rx_dgs30xx.search(platform):
            config = self.cli("show config current_config")
            config = self.strip_first_lines(config, 1)
            return self.cleaned_config(config)

        # DES-1210-28/ME/B2, DES-1210-26/ME, DES-1210-10/ME, etc.
        if self.rx_des1210me.search(platform):
            config = self.cli("show config current_config")
            config = self.strip_first_lines(config, 4)
            config = re.sub(r"config time \d+[^\n]*\n", "", config)
            while config.endswith("\n\n"):
                config = config[:-1]
            return self.cleaned_config(config)

        # DGS-1100-06/ME
        if self.rx_dgs1100_06me.search(platform):
            config = self.cli("show config current_config")
            config = self.strip_first_lines(config, 4)
            config = re.sub(r"config time \d+[^\n]*\n", "", config)
            while config.endswith("\n\n"):
                config = config[:-1]
            return self.cleaned_config(config)

        # DES-1210-28, DES-1210-52, DES-1210-28/ME/A1
        if self.rx_not_supported1.search(platform):
            raise self.NotSupportedError()

        # DES-3226, DES-3226L, DES-3226S, DES-3250TG
        if self.rx_not_supported2.search(platform):
            raise self.NotSupportedError()

        # DES-3326, DES-3326S, DES-3326SR, DES-3350SR, DES-3350TG, DES-3352SR
        if self.rx_not_supported3.search(platform):
            raise self.NotSupportedError()

        # Last resort
        try:
            config = self.cli("show config current_config")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
