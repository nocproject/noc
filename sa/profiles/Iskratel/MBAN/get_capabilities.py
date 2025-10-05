# ---------------------------------------------------------------------
# Iskratel.MBAN.get_capabilities_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Iskratel.MBAN.get_capabilities"

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has stp enabled
        """
        r = self.cli("show stp")
        return "Spanning Tree Protocol : Disabled" not in r
