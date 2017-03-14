# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.MA5300.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

"""
"""
# Python modules
import re
from collections import defaultdict
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Huawei.MA5300.get_interfaces"
    interface = IGetInterfaces

    rx_iface_sep = re.compile(r"^ Vlan ID",
        re.MULTILINE | re.IGNORECASE)
    rx_vlan_id = re.compile(r"^: (?P<vlanid>\d+)$",
        re.MULTILINE | re.IGNORECASE)
    rx_port = re.compile("(?P<port>(Adsl|Ethernet)\d+/\d+/\d+)")

    def execute(self):
        # ADSL ports
        i = []
        sub = []
        v = self.cli("show switchport trunk").split("  ")
        for data in v:
            match = self.rx_port.search(data)
            if match:
              name =match.group("port")
              sub = [{
                        "name": name,
                        "admin_status": True,
                        "oper_status": True,
#                        "enabled_afi": ["ATM", "BRIDGE"],
                        "enabled_afi": ["BRIDGE"],
#                        "description": description,
                        "untagged_vlan": 1,
#                        "vpi": vpi,
#                        "vci": vci
                      }]
              i += [{
                "name": name,
                "type": "physical",
                "admin_status": True,
                "oper_status": True,
                "subinterfaces": sub,
              }]
        return [{"interfaces": i}]

