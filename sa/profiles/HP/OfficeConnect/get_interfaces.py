# ---------------------------------------------------------------------
# HP.OfficeConnect.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "HP.OfficeConnect.get_interfaces"
    interface = IGetInterfaces

    SNMP_IF_DESCR_TABLE = "IF-MIB::ifName"
