# ---------------------------------------------------------------------
# OS.Linux.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "OS.Linux.get_capabilities"

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp/ladvd daemon enabled
        """
        r1 = self.cli("/bin/ps aux | grep [l]advd")
        r2 = self.cli("/bin/ps aux | grep [l]ldpd")

        return bool(r1 or r2)

    @false_on_cli_error
    def has_cdp_cli(self):
        """
        Check box has cdp enabled
        """
        # Ladvd daemon always listen CDP
        r1 = self.cli("/bin/ps aux | grep [l]advd")

        # for lldpd daemon need check CDP enable in config. LLDPD_OPTIONS="-c" in /etc/sysconfig/lldpd
        r2 = self.cli('/bin/ps aux | grep "[/]usr/sbin/lldpd -c"')

        return bool(r1 or r2)
