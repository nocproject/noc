# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Juniper.JUNOS.get_vlans"
    interface = IGetVlans

    rx_vlan_line = re.compile(
        r"^((?P<routing_instance>\S+)\s+)?(?P<name>\S+)\s+(?P<vlan_id>[1-9][0-9]*)",
        re.MULTILINE
    )

    def execute(self):
        if not self.is_switch or not self.profile.command_exist(self, "vlans"):
            return []
        return self.cli("show vlans brief", list_re=self.rx_vlan_line)
=======
##----------------------------------------------------------------------
## Juniper.JUNOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "Juniper.JUNOS.get_vlans"
    implements = [IGetVlans]

    rx_vlan_line = re.compile(r"^(?P<name>\S+)\s+(?P<vlan_id>\d+)\s+")

    def execute(self):
        return self.cli("show vlan brief", list_re=self.rx_vlan_line)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
