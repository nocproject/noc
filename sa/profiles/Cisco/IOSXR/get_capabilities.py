# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOSXR.get_capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Cisco.IOSXR.get_capabilities"

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp neighbors")
        return "% LLDP is not enabled" not in r

    @false_on_cli_error
    def has_cdp(self):
        """
        Check box has cdp enabled
        """
        r = self.cli("show cdp neighbors")
        return "% CDP is not enabled" not in r

    @false_on_cli_error
    def has_oam(self):
        """
        Check box has oam enabled
        """
        r = self.cli("show ethernet oam summary")
        return "There are no interfaces with Ethernet Link OAM configured" not in r  # @todo:  not tested
