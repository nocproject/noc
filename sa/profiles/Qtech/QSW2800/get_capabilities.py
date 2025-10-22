# ---------------------------------------------------------------------
# Qtech.QSW2800.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error
from noc.core.mib import mib


class Script(BaseScript):
    name = "Qtech.QSW2800.get_capabilities"

    rx_iface = re.compile(r"^\s*(?P<ifname>Ethernet\d+/\d+)\s+is\s+(?:up|down)", re.MULTILINE)
    rx_oam = re.compile(r"Doesn\'t (support efmoam|enable EFMOAM!)")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp", cached=True)
        return "LLDP has been enabled globally" in cmd

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has lldp enabled on Qtech
        """
        r = self.snmp.get(mib["LLDP-MIB::lldpStatsRemTablesInserts", 0])
        if r:
            return True

    @false_on_snmp_error
    def has_snmp_enterprises(self):
        """
        Check box oid 1.3.6.1.4.1.27514 or 1.3.6.1.4.1.6339
        """
        x = self.snmp.get(mib["SNMPv2-MIB::sysObjectID", 0])
        if x:
            return int(x.split(".")[6])

    @false_on_snmp_error
    def has_snmp_memory_oids(self, oid):
        """
        Check box has memory usage 1.3.6.1.4.1.27514.100.1.11.11.0 enabled on Qtech
        """
        x = self.snmp.get("1.3.6.1.4.1." + str(oid) + ".100.1.11.11.0")
        if x:
            return True

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        # Spanning Tree Enabled/Disabled : Enabled
        cmd = self.cli("show spanning-tree")
        return "STP is disabled" not in cmd

    @false_on_snmp_error
    def has_stp_snmp(self):
        """
        Check box has STP enabled
        """
        # Spanning Tree Enabled/Disabled : Enabled
        r = self.snmp.getnext(mib["BRIDGE-MIB::dot1dStpPortEnable"], bulk=False)
        # if value == 1:
        return any(x[1] for x in r)

    @false_on_cli_error
    def has_oam_cli(self):
        """
        Check box has OAM enabled
        """
        v = self.cli("show interface", cached=True)
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
        if self.has_snmp():
            f = self.has_snmp_enterprises()
            if f:
                caps["SNMP | OID | EnterpriseID"] = f
                m = self.has_snmp_memory_oids(f)
                if m:
                    caps["Qtech | OID | Memory Usage 11"] = True

    def execute_platform_snmp(self, caps):
        f = self.has_snmp_enterprises()
        if f:
            caps["SNMP | OID | EnterpriseID"] = f
            m = self.has_snmp_memory_oids(f)
            if m:
                caps["Qtech | OID | Memory Usage 11"] = True
