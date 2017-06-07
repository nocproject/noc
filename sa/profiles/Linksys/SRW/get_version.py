# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linksys.SWR.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    """
    Try to log in
    """
    name = "Linksys.SWR.get_version"
    interface = IGetVersion
    requires = []

    def execute(self):
        # @todo Object parser
        if self.has_snmp():
            version = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.10.67108992")
            platform = self.snmp.get("1.3.6.1.2.1.47.1.1.1.1.7.68420352")
            return {"vendor": "Linksys",
                    "version": version,
                    "platform": platform}
        else:
            return {"vendor": "Linksys",
                    "version": "",
                    "platform": "Unknown"}
