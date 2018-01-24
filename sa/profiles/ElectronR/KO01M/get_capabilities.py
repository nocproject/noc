# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ElectronR.KO01M.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "ElectronR.KO01M.get_capabilities"

    def execute(self):
        """
        Check basic SNMP support
        """
        return {
            'SNMP': True,
            "SNMP | Bulk": False,
            'SNMP | v1': True,
            'SNMP | v2c': True,
            'SNMP | v3': False}
