# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# TPLink.EAP.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mib import mib


class Script(BaseScript):
    name = "TPLink.EAP.get_chassis_id"
    cache = True
    interface = IGetChassisID

    SNMP_GETNEXT_OIDS = {"SNMP": [mib["IF-MIB::ifPhysAddress"]]}
