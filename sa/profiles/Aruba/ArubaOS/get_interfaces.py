# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Aruba.ArubaOS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(NOCScript):
    name = "Aruba.ArubaOS.get_interfaces"
    implements = [IGetInterfaces]

    type_map = {
        "et": "physical",
        "ma": "management",
        "vl": "SVI",
        "po": "aggregated",
        "lo": "loopback"
    }

    rx_iface = re.compile(
        r"^(?P<name>\S+) is \S+, line protocol is \S+\n"
        r"Hardware is [^,]+, address is (?P<mac>\S+)",
        re.MULTILINE | re.DOTALL
    )

    def execute(self, interface=None):
        interfaces = []
        # Ethernet ports
        v = self.cli("show interface")
        for match in self.rx_iface.finditer(v):
            interfaces += [{
                "name": match.group("name"),
                "type": "physical",
                "mac": match.group("mac"),
                "subinterfaces": []
            }]
        return [{"interfaces": interfaces}]
