# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_capabilities_ex
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.lib.mib import mib


class Script(BaseScript):
    name = "Linux.RHEL.get_capabilities"

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp\ladvd daemon enabled
        """
        r1 = self.cli("/bin/ps aux | grep [l]advd")
        r2 = self.cli("/bin/ps aux | grep [l]ldpd")

        if r1 or r2:
            return True
        else:
            return False
        
    @false_on_cli_error
    def has_cdp(self):
        """
        Check box has cdp enabled
        """
        # Ladvd daemon always listen CDP
        r1 = self.cli("/bin/ps aux | grep [l]advd")
        
        # for lldpd daemon need check CDP enable in config. LLDPD_OPTIONS="-c" in /etc/sysconfig/lldpd
        r2 = self.cli("/bin/ps aux | grep \"[/]usr/sbin/lldpd -c\"")

        if r1 or r2:
            return True
        else:
            return False


