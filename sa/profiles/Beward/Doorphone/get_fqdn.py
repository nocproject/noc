# ---------------------------------------------------------------------
# Beward.Doorphone.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript

# NOC modules
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Beward.Doorphone.get_fqdn"
    interface = IGetFQDN
