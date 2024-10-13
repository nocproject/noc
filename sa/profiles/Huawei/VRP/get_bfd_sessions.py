# ---------------------------------------------------------------------
# Huawei.VRP.get_bfd_sessions
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetbfdsessions import IGetBFDSessions


class Script(BaseScript):
    name = "Huawei.VRP.get_bfd_sessions"
    interface = IGetBFDSessions

    rx_version = re.compile(
        r"^-+\n"
        r"^.+MIndex\s*:\s*(?P<mindex>\d+).+State\s*:\s*(?P<state>(Up|Down))\s+Name\s*:\s*(?P<name>\S+)\s*\n"
        r"^-+",
        re.MULTILINE,
    )

    rx_neigh = re.compile(
        r"^-+\n"
        r".+State\s*:\s*(?P<state>(Up|Down))\s+Name\s*:\s*(?P<name>\S+)\s*\n"
        r"^-+\n"
        r"^\s*Local\s*Discriminator\s*:\s*(?P<local_discriminator>\d+)\s*"
        r"Remote\s*Discriminator\s*:\s*(?P<remote_discriminator>\d+)\s*\n"
        r"(.+\n)+\s+Bind\sPeer\sIP\sAddress\s*:\s*(?P<remote_address>\S+)\s*\n"
        r"(.+\n)?\s+Bind\sInterface\s*:\s*(?P<local_interface>.+)\s*\n"
        r"(.+\n)+\s+Min\sTx\sInterval\s\(ms\)\s*:\s*(?P<tx_interval>\d+)\s*"
        r"Min\sRx\sInterval\s\(ms\)\s*:\s*(?P<rx_interval>\d+)\s*\n"
        r"(.+\n)+\s+Local\sDetect\sMulti\s*:\s*(?P<multiplier>\d+)\s+"
        r"Detect\sInterval\s\(ms\)\s*:\s*(?P<detect_time>\d+)\s*\n"
        r"(.+\n)+\s+Bind\sApplication\s*:\s*(?P<clients>.+)\s*\n"
        r"(.+\n)+",
        re.MULTILINE | re.IGNORECASE,
    )

    # IOS to interface client type mappings
    client_map = {
        "ISIS": "ISIS",
        "OSPF": "OSPF",
        "BGP": "BGP",
        "EIGRP": "EIGRP",
        "IFNET": "IFNET",
        "BFD": "BFD",
        "RSVP": "RSVP",
        "PIM": "PIM",
    }

    client_ignored = ["CEF", "AUTO", "|"]

    def execute_cli(self, **kwargs):
        r = []
        try:
            s = self.cli("display bfd session all verbose")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        for match in self.rx_neigh.finditer(s):
            r += [
                {
                    "remote_address": match.group("remote_address").strip(),
                    "local_interface": match.group("local_interface").strip(),
                    "local_discriminator": int(match.group("local_discriminator")),
                    "remote_discriminator": int(match.group("remote_discriminator")),
                    "state": match.group("state").upper(),
                    "clients": [
                        self.client_map[c]
                        for c in match.group("clients").split()
                        if c not in self.client_ignored
                    ],
                    # Convert microsecond
                    "tx_interval": int(match.group("tx_interval")) * 1000,
                    "multiplier": int(match.group("multiplier")),
                    # Convert microsecond
                    "detect_time": int(match.group("detect_time")) * 1000,
                }
            ]
        return r
