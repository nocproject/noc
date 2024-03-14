# ---------------------------------------------------------------------
# Telecom.CPE.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2023-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Telecom.CPE.get_fqdn"
    interface = IGetFQDN
