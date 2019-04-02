# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ericsson.SEOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Ericsson.SEOS.get_chassis_id"
    cache = True
    interface = IGetChassisID
