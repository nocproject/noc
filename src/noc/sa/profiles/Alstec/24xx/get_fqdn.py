# ---------------------------------------------------------------------
# Alstec.24xx.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "Alstec.24xx.get_fqdn"
    interface = IGetFQDN

    def execute_cli(self):
        # Getting pattern prompt
        self.cli("")
        v = self.get_cli_stream()
        pattern = smart_text(v.patterns["prompt"].pattern)
        return pattern.split(r"\(", 1)[1].split("\\)", 1)[0].replace("\\", "")
