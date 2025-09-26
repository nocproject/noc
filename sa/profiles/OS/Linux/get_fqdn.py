# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OS.Linux.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "OS.Linux.get_fqdn"
    interface = IGetFQDN

    always_prefer = "S"

    def execute_cli(self, **kwargs):
        return self.cli("uname -n").strip()
