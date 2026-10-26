# ---------------------------------------------------------------------
# Ruckus.SmartZone.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.mib import mib
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript


class Script(BaseScript):
    name = "Ruckus.SmartZone.get_chassis_id"
    cache = True
    interface = IGetChassisID

    SNMP_GET_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress", 4]]}
