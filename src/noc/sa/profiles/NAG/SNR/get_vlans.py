# ---------------------------------------------------------------------
# NAG.SNR.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.sa.profiles.Generic.get_vlans import Script as BaseScript


class Script(BaseScript):
    name = "NAG.SNR.get_vlans"
    interface = IGetVlans
