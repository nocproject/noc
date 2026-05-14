# ----------------------------------------------------------------------
# C3Solution.PDU.get_version
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "C3Solution.PDU.get_version"
    cache = True
    interface = IGetVersion

    def execute_snmp(self, **kwargs):
        return {"vendor": "C3Solution", "platform": "RPDU A", "version": "1.5.2"}
