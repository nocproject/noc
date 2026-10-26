# ---------------------------------------------------------------------
# Huawei.MA5600T.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.interfaces.igetfqdn import IGetFQDN
from noc.sa.profiles.Generic.get_fqdn import Script as BaseScript


class Script(BaseScript):
    name = "Huawei.MA5600T.get_fqdn"
    interface = IGetFQDN
