# ---------------------------------------------------------------------
# Iskratel.ESCOM.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Iskratel.ESCOM.get_fqdn"
    interface = IGetFQDN
    always_prefer = "S"
