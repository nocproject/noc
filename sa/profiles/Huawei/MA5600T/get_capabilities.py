# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "Huawei.MA5600T.get_capabilities"

    CHECK_SNMP_GETNEXT = {"SNMP | MIB | ADSL-MIB": mib["ADSL-LINE-MIB::adslLineCoding"]}

    rx_lacp_id = re.compile(r"^\s+(?P<id>\d+)\s+\d+", re.MULTILINE)

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        # Spanning Tree Enabled/Disabled : Enabled
        cmd = self.cli("display current-configuration section config")
        return "stp enable" in cmd

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check box has LACP enabled
        """
        cmd = self.cli("display lacp link-aggregation summary")
        return self.rx_lacp_id.search(cmd) is not None

    @false_on_cli_error
    def has_olt_cli(self):
        cmd = self.cli("display ont global-config")
        return bool(cmd)

    @false_on_cli_error
    def has_olt_snmp(self):
        cmd = self.snmp.get(mib["HUAWEI-XPON-MIB::hwGponDeviceDbaAssignmentMode", 0])
        return bool(cmd)

    def execute_platform_cli(self, caps):
        if self.has_olt_cli():
            caps["Network | PON | OLT"] = True

    def execute_platform_snmp(self, caps):
        if self.has_olt_snmp():
            caps["Network | PON | OLT"] = True
