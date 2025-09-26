# ---------------------------------------------------------------------
# Qtech.QSW2800.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "Qtech.QSW2800.get_fqdn"
    interface = IGetFQDN
    always_prefer = "S"

    rx_hostname = re.compile(r"^hostname (?P<hostname>\S+)$", re.MULTILINE)

    def execute_cli(self):
        # Getting pattern prompt
        v = self.get_cli_stream()
        pattern = smart_text(v.patterns["prompt"].pattern)
        return pattern.split("(?")[0][1:].replace("\\", "")
