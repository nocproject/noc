# ---------------------------------------------------------------------
# OS.FreeBSD.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "OS.FreeBSD.get_capabilities"

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldpd or ladvd daemon enabled
        """
        return bool(self.cli("/usr/bin/pgrep lldpd") or self.cli("/usr/bin/pgrep ladvd"))
