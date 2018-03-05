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

    oid = "1.3.6.1.2.1.1.1"

    def check_snmp_getnext(self, oid, bulk=False, only_first=True, version=None):
        """
        Check SNMP response to GETNEXT/BULK
        """
        return False
