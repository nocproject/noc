# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_arp import Script as BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_arp"
    interface = IGetARP

    def execute_cli(self):
        arp = []
        for n, f, r in self.cli_detail("/ip arp print detail without-paging"):
            if "mac-address" in r:
                arp += [{
                    "ip": r["address"],
                    "mac": r["mac-address"],
                    "interface": r["interface"]
                }]
            else:
                arp += [{
                    "ip": r["address"],
                    "interface": r["interface"]
                }]
        return arp
=======
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP


class Script(NOCScript):
    name = "MikroTik.RouterOS.get_arp"
    implements = [IGetARP]

    def execute(self):
        return [{
            "ip": r["address"],
            "mac": r["mac-address"],
            "interface": r["interface"]
        } for n, f, r in self.cli_detail(
            "/ip arp print detail without-paging")]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
