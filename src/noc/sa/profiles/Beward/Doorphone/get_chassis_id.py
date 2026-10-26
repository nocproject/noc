# ---------------------------------------------------------------------
# Beward.Doorphone.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript


class Script(BaseScript):
    name = "Beward.Doorphone.get_chassis_id"
    interface = IGetChassisID
    cache = True
