# ---------------------------------------------------------------------
# STerra.Gate.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interface_properties import Script as BaseScript


class Script(BaseScript):
    name = "STerra.Gate.get_interface_properties"

    SNMP_NAME_TABLE = "IF-MIB::ifName"
