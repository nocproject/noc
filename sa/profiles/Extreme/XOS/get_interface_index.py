# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Extreme.XOS.get_interface_index
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetifindex import IGetIfIndex


class Script(BaseScript):
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    """
    Extreme.XOS.get_interface_index
    """
    name = "Extreme.XOS.get_interface_index"
<<<<<<< HEAD
    interface = IGetIfIndex

    rx_ifidx_phys = re.compile(
        "^X\S+\s+Port\s+(?P<port>\d+(\:\d+)?)", re.IGNORECASE)
    rx_ifidx_vlan = re.compile(
        "^VLAN\s+\S+\s+\((?P<port>\S+)\)", re.IGNORECASE)
=======
    implements = [IGetIfIndex]

    rx_ifidx_phys = re.compile("^X\S+\s+Port\s+(?P<port>\d+)", re.IGNORECASE )
    rx_ifidx_vlan = re.compile("^VLAN\s+\S+\s+\((?P<port>\S+)\)", re.IGNORECASE )
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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
<<<<<<< HEAD
                        return int(oid.split(".")[-1])
=======
                      return int(oid.split(".")[-1])
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                match = self.rx_ifidx_vlan.match(v)
                if match:
                    v = match.group("port")
                    if v == interface:
<<<<<<< HEAD
                        return int(oid.split(".")[-1])
=======
                      return int(oid.split(".")[-1])
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        except self.snmp.TimeOutError:
            return None
