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
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "Huawei.MA5600T.get_capabilities"

    CHECK_SNMP_GETNEXT = {"SNMP | MIB | ADSL-MIB": mib["ADSL-LINE-MIB::adslLineCoding"]}

    SNMP_NONE_VALUE = 2147483647

    # Stuck respons on command and broken next script on discovery
    keep_cli_session = False

    rx_lacp_id = re.compile(r"^\s+(?P<id>\d+)\s+\d+", re.MULTILINE)

    rx_lldp_enable = re.compile(r"LLDP\sstatus\s+:\s*enabled")

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
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        cmd = self.cli("display lldp local")
        return self.rx_lldp_enable.search(cmd) is not None

    @false_on_cli_error
    def has_olt_cli(self):
        cmd = self.cli("display ont global-config")
        return bool(cmd)

    @false_on_snmp_error
    def has_olt_snmp(self):
        cmd = self.snmp.get(mib["HUAWEI-XPON-MIB::hwGponDeviceDbaAssignmentMode", 0])
        return bool(cmd)

    @false_on_snmp_error
    def has_slot_temperature(self):
        r = []
        for oid, value in self.snmp.getnext("1.3.6.1.4.1.2011.6.3.3.2.1.13"):
            if value == self.SNMP_NONE_VALUE:
                continue
            r += [oid.split(".")[-1]]
        return r

    def get_mac_table_cli(self):
        """
        Check box has 'display mac-address' command supported
        """
        try:
            self.cli("display mac-address number")
        except self.CLISyntaxError:
            return False
        return True

    def execute_platform_cli(self, caps):
        if self.has_olt_cli():
            caps["Network | PON | OLT"] = True
        r = self.has_slot_temperature()
        if r:
            caps["Slot | Member Ids | Temperature"] = " | ".join(r)
        r = self.get_mac_table_cli()
        if r:
            caps["Huawei | MA5600T | CLI | MAC"] = True

    def execute_platform_snmp(self, caps):
        if self.has_olt_snmp():
            caps["Network | PON | OLT"] = True
        r = self.has_slot_temperature()
        if r:
            caps["Slot | Member Ids | Temperature"] = " | ".join(r)
