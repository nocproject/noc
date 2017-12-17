# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.RG.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.RG.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        version = None
        if self.has_snmp():
            c = self.snmp.get(mib["SNMPv2-MIB::sysDescr", 0])
            version = c.split()[2]
            p = self.snmp.get(mib["SNMPv2-MIB::sysObjectID", 0])
            platform = self.profile.get_platforms(p.split(".")[-1])
        return {
            "vendor": "Eltex",
            "platform": platform,
            "version": version
        }
