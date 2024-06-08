# ---------------------------------------------------------------------
# HP.ProCurve.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "HP.ProCurve.get_fqdn"
    interface = IGetFQDN
