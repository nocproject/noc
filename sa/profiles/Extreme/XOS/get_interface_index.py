# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_interface_index
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetIfIndex


class Script(NOCScript):
    """
    Extreme.XOS.get_interface_index
    """
    name = "Extreme.XOS.get_interface_index"
    implements = [IGetIfIndex]

    rx_ifidx_phys = re.compile("^X\S+\s+Port\s+(?P<port>\d+)", re.IGNORECASE )
    rx_ifidx_vlan = re.compile("^VLAN\s+\S+\s+\((?P<port>\S+)\)", re.IGNORECASE )

    requires = []

    def execute(self, interface):
        try:
            # 1.3.6.1.2.1.2.2.1.1 - IF-MIB::ifDescr
            for oid, v in self.snmp.getnext("1.3.6.1.2.1.2.2.1.2"):
                v = self.profile.convert_interface_name(v)
                match = self.rx_ifidx_phys.match(v)
                if match:
                    v = match.group("port")
                    if v == interface:
                      return int(oid.split(".")[-1])
                match = self.rx_ifidx_vlan.match(v)
                if match:
                    v = match.group("port")
                    if v == interface:
                      return int(oid.split(".")[-1])
        except self.snmp.TimeOutError:
            return None
