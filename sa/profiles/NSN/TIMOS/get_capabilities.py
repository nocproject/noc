# ----------------------------------------------------------------------
# NSN.TIMOS.get_capabilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error, false_on_snmp_error
from noc.core.mib import mib
from noc.core.validators import is_int


class Script(BaseScript):
    name = "NSN.TIMOS.get_capabilities"
    cache = True

    CHECK_SNMP_GET = {
        "BRAS | IPoE": "1.3.6.1.4.1.6527.3.1.2.33.1.107.1.65.1",
        "BRAS | PPPoE": "1.3.6.1.4.1.6527.3.1.2.33.5.9.1.2.1",
        "Network | DHCP": "1.3.6.1.4.1.6527.3.1.2.47.1.21.0",  # tmnxDhcpSvrNumLeases
    }
    rx_lldp = re.compile(r"Admin Enabled\s+: True")
    rx_port = re.compile(
        r"^(?P<port>\d+/\d+/\d+)\s+(?:Up|Down)\s+(?:Yes|No)\s+"
        r"(?:Up|Down|Link Up)\s+\d+\s+\d+\s+(?:\d+|\-)\s+\S+\s+\S+\s+"
        r"(?:xgige|xcme)",
        re.MULTILINE,
    )
    rx_oam = re.compile(r"Admin State\s+: up", re.MULTILINE)

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show system lldp | match Admin")
        return self.rx_lldp.search(cmd) is not None

    @false_on_snmp_error
    def has_lldp_snmp(self):
        """
        Check box has lldp enabled
        """
        r = self.snmp.get(mib["LLDP-MIB::lldpLocChassisIdSubtype", 0])
        return is_int(r) and r >= 1

    @false_on_cli_error
    def has_oam_cli(self):
        """
        Check box has oam enabled
        """
        for match in self.rx_port.finditer(self.cli("show port")):
            cmd = self.cli("show port %s ethernet efm-oam" % match.group("port"))
            match1 = self.rx_oam.search(cmd)
            if match1:
                return True
        return False

    @false_on_cli_error
    def has_bfd_cli(self):
        """
        Check box has bfd enabled
        """
        cmd = self.cli("show router bfd interface")
        return "No Matching Entries Found" not in cmd

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check stack members
        :return:
        """
        r = self.cli("show lag statistics")
        return r
