# ---------------------------------------------------------------------
# MikroTik.RouterOS.get_capabilities_ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript, false_on_cli_error


class Script(BaseScript):
    name = "MikroTik.RouterOS.get_capabilities"
    cache = True

    rx_discover_interfaces = re.compile(
        r"discover-interface-list: (?P<list>\S+)\s*\n", re.MULTILINE
    )
    rx_lldp = re.compile(r"(?:lldp\s*\n|protocol: .*lldp)", re.MULTILINE)
    rx_cdp = re.compile(r"(?:cdp\s*\n|protocol: cdp)", re.MULTILINE)

    def execute_platform_cli(self, caps):
        c = self.scripts.get_license()
        caps["MikroTik | RouterOS | License | SoftwareID"] = c["software-id"]
        caps["MikroTik | RouterOS | License | Level"] = c["nlevel"]
        if c.get("upgradable-to"):
            caps["MikroTik | RouterOS | License | Upgradable To"] = c["upgradable-to"]

    def has_cdp_cli(self):
        """
        Check box has cdp enabled
        """
        c = self.cli("/ip neighbor discovery-settings print without-paging", cached=True)
        if self.rx_discover_interfaces.search(c)["list"] != "none":
            return self.rx_cdp.search(c) is not None
        return False

    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        c = self.cli("/ip neighbor discovery-settings print without-paging", cached=True)
        if self.rx_discover_interfaces.search(c)["list"] != "none":
            return self.rx_lldp.search(c) is not None
        return False

    @false_on_cli_error
    def has_ipv6_cli(self):
        """
        Check box has lldp enabled
        """
        return bool(self.cli_detail("/ipv6 nd print detail without-paging"))
