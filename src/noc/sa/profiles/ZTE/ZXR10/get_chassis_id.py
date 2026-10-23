# ---------------------------------------------------------------------
# ZTE.ZXR10.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "ZTE.ZXR10.get_chassis_id"
    interface = IGetChassisID
    cache = True
    always_prefer = "S"
