# ---------------------------------------------------------------------
# DLink.DxS.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "DLink.DxS.get_fqdn"
    interface = IGetFQDN

    rx_name = re.compile(r"^System [Nn]ame\s+:(?P<name>.*)$", re.MULTILINE)

    def execute_cli(self):
        v = self.scripts.get_switch()
        return self.rx_name.search(v).group("name").strip()
