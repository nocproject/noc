# ---------------------------------------------------------------------
# Ericsson.SEOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mib import mib


class Script(BaseScript):
    name = "Ericsson.SEOS.get_interfaces"
    cache = True
    interface = IGetInterfaces

    INTERFACE_TYPES = {
        1: "physical",
        6: "physical",  # ethernetCsmacd
        18: "physical",  # E1 - ds1
        23: "physical",  # ppp
        24: "loopback",  # softwareLoopback
        117: "physical",  # gigabitEthernet
        131: "tunnel",  # tunnel
        135: "SVI",  # l2vlan
        161: "aggregated",  # ieee8023adLag
        53: "SVI",  # propVirtual
        54: "physical",  # propMultiplexor
    }

    def clean_iftype(self, ifname: str, ifindex: Optional[int] = None) -> str:
        if not getattr(self, "_iftype_map", None):
            self._iftype_map = {
                int(oid.split(".")[-1]): iftype
                for oid, iftype in self.snmp.getnext(mib["IF-MIB::ifType"])
            }
        return self.INTERFACE_TYPES.get(self._iftype_map[ifindex], "other")

    def is_subinterface(self, iface):
        return False
