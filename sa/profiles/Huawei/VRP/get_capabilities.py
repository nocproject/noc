# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Huawei.VRP.get_capabilities"

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has STP enabled
        """
        try:
            r = self.cli("display stp global | include Enabled")
            return "Enabled" in r
        except self.CLISyntaxError:
            r = self.cli("display stp | include disabled")
            return not "Protocol Status" in r

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has LLDP enabled
        """
        r = self.cli("display lldp local | include enabled")
        return not "Global LLDP is not enabled" in r

    @false_on_cli_error
    def has_bfd(self):
        """
        Check box has BFD enabled
        """
        r = self.cli("display bfd configuration all")
        return not "Please enable BFD in global mode first" in r

    @false_on_cli_error
    def has_udld(self):
        """
        Check box has UDLD enabled
        """
        r = self.cli("display dldp")
        return not "Global DLDP is not enabled" in r
