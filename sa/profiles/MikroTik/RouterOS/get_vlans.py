# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_vlans"
    interface = IGetVlans

    def execute(self):
        try:
            v = self.cli_detail("interface ethernet switch vlan print detail")
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        return  [{"vlan_id": d["vlan-id"]} for n, f, d in v if not f]
