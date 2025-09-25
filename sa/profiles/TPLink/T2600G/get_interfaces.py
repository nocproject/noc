# ---------------------------------------------------------------------
# TPLink.T2600G..get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "TPLink.T2600G.get_interfaces"
    interface = IGetInterfaces

    MAX_REPETITIONS = 10
