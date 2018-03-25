# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2800.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Qtech.QSW2800.get_capabilities"

    rx_iface = re.compile(
        "^\s*(?P<ifname>Ethernet\d+/\d+)\s+is\s+(?:up|down)", re.MULTILINE)
    rx_oam = re.compile(r"Doesn\'t (support efmoam|enable EFMOAM!)")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp")
        return "LLDP has been enabled globally" in cmd

    def has_lldp_snmp(self):
        """
        Check box has lldp enabled on Qtech
        """
        try:
            r = self.snmp.get("1.0.8802.1.1.2.1.2.2.0")
            if r > 0:
                return True
        except self.snmp.TimeOutError:
            return False

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        # Spanning Tree Enabled/Disabled : Enabled
        cmd = self.cli("show spanning-tree")
        return "STP is disabled" not in cmd

    @false_on_cli_error
    def has_oam_cli(self):
        """
        Check box has OAM enabled
        """
        v = self.cli("show interface | include Ethernet")
        for match in self.rx_iface.finditer(v):
            try:
                cmd = self.cli("show ethernet-oam local interface %s" % match.group("ifname"))
                match = self.rx_oam.search(cmd)
                if not match:
                    return True
            except self.CLISyntaxError:
                return False
        return False

    @false_on_cli_error
    def has_stack(self):
        """
        Check stack members
        :return:
        """
        r = self.cli("show slot")
        return [l.splitlines()[0].split(":")[1].strip("-") for l in r.split("\n----") if l]

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check stack members
        :return:
        """
        r = self.cli("show port-group brief")
        return "active" in r

    def execute_platform_cli(self, caps):
        s = self.has_stack()
        if s:
            caps["Stack | Members"] = len(s) if len(s) != 1 else 0
            caps["Stack | Member Ids"] = " | ".join(s)
