# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.TIMOS.get_capabilities_ex
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "Alcatel.TIMOS.get_capabilities"

    CHECK_SNMP_GET = {
        "BRAS | IPoE": "1.3.6.1.4.1.6527.3.1.2.33.1.107.1.65.1"
    }
