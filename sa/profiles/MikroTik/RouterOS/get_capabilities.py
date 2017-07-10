# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_capabilities_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript, false_on_cli_error


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_capabilities"
    cache = True

    def execute_platform(self, caps):
        c = self.scripts.get_license()
        caps["MikroTik | RouterOS | License | SoftwareID"] = c["software-id"]
        caps["MikroTik | RouterOS | License | Level"] = c["nlevel"]
        if c.get("upgradable-to"):
            caps["MikroTik | RouterOS | License | Upgradable To"] = c["upgradable-to"]

    def has_cdp(self):
        """
        Check box has cdp enabled
        """
        return True

    @false_on_cli_error
    def has_ipv6(self):
        """
        Check box has lldp enabled
        """
        return bool(self.cli_detail("/ipv6 nd print detail without-paging"))
