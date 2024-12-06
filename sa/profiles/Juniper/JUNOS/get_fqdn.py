# ---------------------------------------------------------------------
# Juniper.JUNOS.get_fqdn
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
    name = "Juniper.JUNOS.get_fqdn"
    interface = IGetFQDN

    rx_config = re.compile(
        r"^host-name (?P<hostname>\S+);\s*\n(?:^domain-name (?P<dname>\S+);)?", re.MULTILINE
    )

    def execute_cli(self):
        v = self.cli("show configuration system | match -name", cached=True)
        match = self.rx_config.search(v)
        if match:
            fqdn = match.group("hostname")
            if match.group("dname"):
                fqdn = "%s.%s" % (fqdn, match.group("dname"))
            return fqdn
        raise NotImplementedError
