# ---------------------------------------------------------------------
# Sumavision.IPQAM.get_uptime
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_uptime import Script as BaseScript


class Script(BaseScript):
    """
    Returns system uptime in seconds
    """

    name = "Sumavision.IPQAM.get_uptime"

    UPTIME_MULTIPLIER = 800.0
