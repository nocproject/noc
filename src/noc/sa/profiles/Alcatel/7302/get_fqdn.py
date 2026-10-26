# ---------------------------------------------------------------------
# Alcatel.7302.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.interfaces.igetfqdn import IGetFQDN
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript


class Script(BaseScript):
    name = "Alcatel.7302.get_fqdn"
    interface = IGetFQDN
