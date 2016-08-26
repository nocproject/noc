# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOSe.get_capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Juniper.JUNOSe.get_capabilities"

    @false_on_cli_error
    def has_oam(self):
        """
        Check box has oam enabled
        """
        r = self.cli("show ethernet oam lfm summary")
        return bool(r)

    @false_on_cli_error
    def has_bfd(self):
        """
        Check box has BFD enabled
        """
        r = self.cli("show bfd session")
        return not "not found or down" in r
