# ----------------------------------------------------------------------
# Mellanox.Onyx.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Mellanox.Onyx.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^(?P<ifname>Eth\S+):\s*\n"
        r"^\s+Admin state\s+: (?P<admin_state>\S+)\s*\n"
        r"^\s+Operational state\s+: (?P<oper_state>\S+)\s*\n"
        r"^\s+Last change in operational status: .+\n"
        r"^\s+Boot delay time\s+: \d+ sec\s*\n"
        r"^\s+Description\s+: (?P<description>.+)\n"
        r"^\s+Mac address\s+: (?P<mac>\S+)\s*\n"
        r"^\s+MTU\s+: (?P<mtu>\d+)",
        re.MULTILINE,
    )

    def execute_cli(self):
        interfaces = []
        c = self.cli("show interfaces", cached=True)
        for match in self.rx_iface.finditer(c):
            iface = {
                "name": match.group("ifname"),
                "type": "physical",
                "admin_status": match.group("admin_state") == "Enabled",
                "oper_status": match.group("oper_state") == "Up",
                "mac": match.group("mac"),
                "subinterfaces": [{
                    "name": match.group("ifname"),
                    "admin_status": match.group("admin_state") == "Enabled",
                    "oper_status": match.group("oper_state") == "Up",
                    "mac": match.group("mac"),
                    "mtu": match.group("mtu"),
                }]
            }
            if match.group("description").strip() != "N/A":
                iface["description"] = match.group("description").strip()
            interfaces += [iface]

        return [{"interfaces": interfaces}]
