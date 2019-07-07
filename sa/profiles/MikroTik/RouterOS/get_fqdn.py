# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_fqdn"
    interface = IGetFQDN

    def execute(self):
        s = self.cli("/system identity print")
        if s and "name: " in s:
            return s.split(":", 1)[1].strip()
        else:
            return "MikroTik"
