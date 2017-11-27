# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
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
        r"^((?P<routing_instance>\S+)\s+)?(?P<name>\S+)\s+(?P<vlan_id>\d+)\s+")

    def execute(self):
        try:
            self.cli("show vlans")
        except self.CLISyntaxError:
            # Juniper do not clear wrong input line
            self.cli("\x08\x08\x08\x08\x08\x08\x08\x08\x08\x08")
            return []
        return self.cli("show vlans brief", list_re=self.rx_vlan_line)
