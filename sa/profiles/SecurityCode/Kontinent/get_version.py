# ---------------------------------------------------------------------
# SecurityCode.Kontinent.get_version
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetversion import IGetVersion


class Script(BaseScript):
    name = "SecurityCode.Kontinent.get_version"
    interface = IGetVersion

    def execute_snmp(self):
        return {"vendor": "SecurityCode", "version": None, "platform": "Kontinent"}
