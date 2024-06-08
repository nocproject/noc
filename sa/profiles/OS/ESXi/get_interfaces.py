# ---------------------------------------------------------------------
# OS.ESXi.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.mib import mib


class Script(BaseScript):
    name = "OS.ESXi.get_interfaces"
    interface = IGetInterfaces

    def clean_iftype(self, ifname, ifindex):
        iftype = self.snmp.get(mib["IF-MIB::ifType", ifindex], cached=True)
        return self.profile.get_interface_type(iftype)
