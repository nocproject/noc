# ----------------------------------------------------------------------
# Raisecom.ROS.get_interface_properties script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_properties import Script as BaseScript
from noc.sa.interfaces.igetinterfaceproperties import IGetInterfaceProperties


class Script(BaseScript):
    name = "Raisecom.ROS.get_interface_properties"
    interface = IGetInterfaceProperties
    requires = []

    def execute(self, **kwargs):
        if self.is_ifname_use or self.is_iscom2624g:
            self.SNMP_NAME_TABLE = "IF-MIB::ifName"
        return super().execute(**kwargs)
