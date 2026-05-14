# ---------------------------------------------------------------------
# C3Solution.PDU.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import List

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mib import mib


class Script(BaseScript):
    name = "C3Solution.PDU.get_interfaces"
    interface = IGetInterfaces

    def get_hints(self, ifname: str, iftype: str) -> List[str]:
        if ifname.startswith("eth"):
            return ["noc::interface::role::uplink"]

    def clean_iftype(self, ifname, ifindex):
        iftype = self.snmp.get(mib["IF-MIB::ifType", ifindex], cached=True)
        return self.profile.get_interface_type(iftype)
