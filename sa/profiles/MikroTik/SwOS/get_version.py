# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.core.mib import mib
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "MikroTik.SwOS.get_version"
    cache = True
    interface = IGetVersion

    def execute(self):
        platform = self.snmp.get(mib["SNMPv2-MIB::sysDescr.0"])

        r = {
            "vendor": "MikroTik",
            "platform": platform,
            "version": "None",
        }
        return r
