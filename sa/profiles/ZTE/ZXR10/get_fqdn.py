# ---------------------------------------------------------------------
# ZTE.ZXR10.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "ZTE.ZXR10.get_fqdn"
    interface = IGetFQDN
    always_prefer = "S"
