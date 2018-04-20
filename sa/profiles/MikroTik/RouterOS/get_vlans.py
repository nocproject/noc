# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_vlans"
    interface = IGetVlans

    def execute(self):
        try:
            v = self.cli_detail(
                "interface ethernet switch vlan print detail without-paging")
        except self.CLISyntaxError:
            return []

        return [{"vlan_id": d["vlan-id"]} for n, f, d in v if not f]
=======
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "MikroTik.RouterOS.get_vlans"
    implements = [IGetVlans]

    def execute(self):
        try:
            v = self.cli_detail("interface ethernet switch vlan print detail")
        except self.CLISyntaxError:
            raise self.NotSupportedError()

        return  [{"vlan_id": d["vlan-id"]} for n, f, d in v if not f]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
