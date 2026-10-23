# ----------------------------------------------------------------------
# Qtech.QSW8200.get_interface_properties script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_properties import Script as BaseScript
from noc.sa.interfaces.igetinterfaceproperties import IGetInterfaceProperties


class Script(BaseScript):
    name = "Qtech.QSW8200.get_interface_properties"
    interface = IGetInterfaceProperties

    SNMP_NAME_TABLE = "IF-MIB::ifName"
