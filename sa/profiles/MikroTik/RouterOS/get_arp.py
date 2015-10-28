# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_arp"
    interface = IGetARP

    def execute(self):
        return [{
            "ip": r["address"],
            "mac": r["mac-address"],
            "interface": r["interface"]
        } for n, f, r in self.cli_detail(
            "/ip arp print detail without-paging")]
