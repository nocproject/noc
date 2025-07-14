# ---------------------------------------------------------------------
# DLink.DxS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error


class Script(BaseScript):
    name = "DLink.DxS.get_capabilities"

    rx_lldp = re.compile(r"LLDP Status\s+: Enabled?")
    rx_stp = re.compile(r"STP Status\s+: Enabled?")
    rx_oam = re.compile(r"^\s*OAM\s+: Enabled", re.MULTILINE)
    rx_stack = re.compile(r"^\s*(?P<box_id>\d+)\s+", re.MULTILINE)

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp", cached=True)
        return self.rx_lldp.search(cmd) is not None

    def has_lldp_snmp(self):
        """
        Check box has lldp enabled
        """
        # Switches with DLINKPRIME-LLDP-EXT-MIB do not support
        # any methods to get local port
        #
        # swL2DevCtrlLLDPState can only get from l2mgmt-mib
        # LLDP-MIB::lldpStatsRemTablesInserts.0
        #
        try:
            r = self.snmp.get("1.0.8802.1.1.2.1.2.2.0")
            if r:
                return True
        except self.snmp.TimeOutError:
            return False

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        # Spanning Tree Enabled/Disabled : Enabled
        if self.is_des_32_33 or self.is_dgs_32_33:
            cmd = self.cli("show stp\nq")
        else:
            cmd = self.cli("show stp", cached=True)
        return self.rx_stp.search(cmd) is not None

    @false_on_cli_error
    def has_oam_cli(self):
        """
        Check box has OAM supported
        """
        if (
            self.is_des_32_33
            or self.is_dgs_32_33
            or self.is_des_3010
            or self.is_des_3018
            or self.is_des_3026
            or self.is_des_35xx
        ):
            return False
        cmd = self.cli("show ethernet_oam ports status")
        return self.rx_oam.search(cmd) is not None

    @false_on_snmp_error
    def has_metric_cpu_usage_oid(self):
        # DLINK-AGENT-MIB::agentCPUutilizationIn5sec
        cpu_oids = ["1.3.6.1.4.1.171.12.1.1.6.1.0"]

        if self.is_des_3200:  # need testing
            cpu_oids += ["1.3.6.1.4.1.171.12.1.1.6.1"]
        # elif self.is_des_1210:
        elif self.is_des_1210_20:
            cpu_oids += ["1.3.6.1.4.1.171.10.76.31.2.100.1.2", "1.3.6.1.4.1.171.10.76.31.1.100.1.2"]
        elif self.is_des_1210_28:
            cpu_oids += [
                "1.3.6.1.4.1.171.10.76.28.1.100.1.2",
                "1.3.6.1.4.1.171.10.76.28.2.100.1.2",
                "1.3.6.1.4.1.171.10.75.15.3.100.2.2",
            ]
        elif self.is_des_3010:
            cpu_oids += ["1.3.6.1.4.1.171.11.63.1.2.2.1.3.2"]
        elif self.is_des_3018:
            cpu_oids += ["1.3.6.1.4.1.171.11.63.2.2.1.3.2"]
        elif self.is_des_3026:
            cpu_oids += ["1.3.6.1.4.1.171.11.63.3.2.1.3.2"]
        elif self.is_dgs_32_33:
            cpu_oids += ["1.3.6.1.4.1.171.11.55.2.2.1.4.1.0"]
        cpu_oids += ["1.3.6.1.4.1.171.10.75.15.2.100.1.1.0"]

        for oid in cpu_oids:
            try:
                r = self.snmp.get(oid)
                if r:
                    return oid
            except Exception:
                pass
        return None

    def execute_platform_cli(self, caps):
        try:
            cmd = self.cli("show stack_device")
            s = []
            for match in self.rx_stack.finditer(cmd):
                s += [match.group("box_id")]
            if s:
                caps["Stack | Members"] = len(s) if len(s) != 1 else 0
                caps["Stack | Member Ids"] = " | ".join(s)
        except self.CLISyntaxError:
            pass
        c = self.has_metric_cpu_usage_oid()
        if c:
            caps["Metrics | OID | CPU | Usage | Value"] = c
