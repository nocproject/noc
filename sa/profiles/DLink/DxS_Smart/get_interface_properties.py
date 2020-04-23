# ----------------------------------------------------------------------
# Generic.get_interface_properties script
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaceproperties import IGetInterfaceProperties


class Script(BaseScript):
    name = "DLink.DxS_Smart.get_interface_properties"
    interface = IGetInterfaceProperties

    SNMP_NAME_TABLE = "IF-MIB::ifName"
