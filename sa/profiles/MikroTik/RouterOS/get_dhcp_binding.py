# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_dhcp_binding
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetDHCPBinding


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_dhcp_binding"
    interface = IGetDHCPBinding

    def execute(self):
        r = []
        now = datetime.datetime.now()
        for n, f, v in self.cli_detail(
            "/ip dhcp-server lease print detail without-paging"):
            r += [{
                "ip": v["address"],
                "mac": v["mac-address"],
                "type": "A",
                "expiration": now  # @todo: Calculate expiration
            }]
        return r
