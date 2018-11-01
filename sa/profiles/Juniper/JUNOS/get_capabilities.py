# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "Juniper.JUNOS.get_capabilities"

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        r = self.cli("show spanning-tree bridge | match Enabled")
        return "?STP" in r

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp | match Enabled")
        return "Enabled" in r

    def has_lldp_snmp(self):
        """
        Check box has lldp enabled
        """
        for v, r in self.snmp.getnext(mib["LLDP-MIB::lldpPortConfigTLVsTxEnable"], bulk=False):
            if r != '\x00':
                return True
        return False

    @false_on_cli_error
    def has_oam_cli(self):
        """
        Check box has oam enabled
        """
        r = self.scripts.get_oam_status()
        return bool(r)

    @false_on_cli_error
    def has_bfd_cli(self):
        """
        Check box has oam enabled
        """
        r = self.cli("show bfd session")
        return "0 sessions, 0 clients" not in r

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check box has lacp enabled
        """
        r = self.cli("show lacp interfaces")
        return "lacp subsystem not running" not in r

    @false_on_cli_error
    def get_rpm_probes(self):
        i = 0
        v = self.scripts.get_sla_probes()
        for p in v:
            i += len(p["tests"])
        return i

    def execute_platform_cli(self, caps):
        np = self.get_rpm_probes()
        caps["Juniper | RPM | Probes"] = np
