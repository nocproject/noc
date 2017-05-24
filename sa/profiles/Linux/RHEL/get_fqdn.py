# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linux.RHEL.get_fqdn
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetfqdn import IGetFQDN


class Script(BaseScript):
    name = "Linux.RHEL.get_fqdn"
    interface = IGetFQDN

    def execute(self):
        if self.has_snmp():
                # and self.access_profile.snmp_ro:
            try:
                # sysName.0
                v = self.snmp.get("1.3.6.1.2.1.1.5.0", cached=True)
                if v:
                   return v
            except self.snmp.TimeOutError:
                pass
        v = self.cli("uname -n").strip()
        fqdn = v
        
        return fqdn
