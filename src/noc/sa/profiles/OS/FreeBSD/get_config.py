# ---------------------------------------------------------------------
# OS.FreeBSD.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetconfig import IGetConfig


class Script(BaseScript):
    name = "OS.FreeBSD.get_config"
    interface = IGetConfig
    rx_not_found = re.compile(r"^cat:.+?No (?:match|such file or directory)")
    configs = ["/etc/rc.conf", "/etc/rc.conf.d/*", "/usr/local/etc/rc.conf.d/*", "/etc/rc.local"]

    def execute_cli(self, **kwargs):
        config = ""
        for c in self.configs:
            conf = self.cli(f"cat -v {c} ; echo")
            match = self.rx_not_found.search(conf)
            if not match:
                config = f"{config}\n## {c}\n{conf}\n"

        config = self.strip_first_lines(config, 1)
        return self.cleaned_config(config)
