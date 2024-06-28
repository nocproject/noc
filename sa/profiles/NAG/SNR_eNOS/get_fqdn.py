# ---------------------------------------------------------------------
# NAG.SNR_eNOS.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript

# NOC modules
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "NAG.SNR_eNOS.get_fqdn"
    interface = IGetFQDN
