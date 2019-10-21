# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ubiquiti.AirOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Ubiquiti.AirOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    SNMP_GET_OIDS = {"SNMP": ["1.2.840.10036.1.1.1.1.5", "1.2.840.10036.2.1.1.1.5"]}
