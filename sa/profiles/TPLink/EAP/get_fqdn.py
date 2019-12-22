# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# TPLink.EAP.get_config
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "TPLink.EAP.get_fqdn"
    interface = IGetFQDN

    def execute_snmp(self, **kwargs):
        v = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
        if v:
            return v
        raise self.NotSupportedError
