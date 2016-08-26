# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MikroTik.RouterOS.get_capabilities_ex
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_capabilities"
    cache = True

    def execute_platform(self, caps):
        c = self.scripts.get_license()
        caps["MikroTik | RouterOS | License | SoftwareID"] = c["software-id"]
        caps["MikroTik | RouterOS | License | Level"] = c["nlevel"]
        if c.get("upgradable-to"):
            caps["MikroTik | RouterOS | License | Upgradable To"] = c["upto"]
