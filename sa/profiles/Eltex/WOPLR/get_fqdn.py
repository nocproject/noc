# ---------------------------------------------------------------------
# Eltex.WOPLR.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Eltex.WOPLR.get_fqdn"
    interface = IGetFQDN
