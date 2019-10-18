# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MSAN.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.mib import mib
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Iskratel.MSAN.get_capabilities"

    SNMP_GET_CHECK_OID = mib["SNMPv2-MIB::sysDescr", 0]

    CHECK_SNMP_GETNEXT = {
        "SNMP | MIB | VDSL2-LINE-MIB": mib["VDSL2-LINE-MIB::xdsl2LineBandStatusLnAtten"]
    }

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp")
        return "disabled on all interfaces" not in cmd
