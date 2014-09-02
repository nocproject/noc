# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_bfd_sessions
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetBFDSessions
from noc.lib.text import find_indented


class Script(NOCScript):
    name = "Juniper.JUNOS.get_bfd_sessions"
    implements = [IGetBFDSessions]

    # JUNOS to interface client type mappings
    client_map = {
        "L2": "L2",
        "RSVP-OAM": "RSVP",
        "ISIS": "ISIS",
        "OSPF": "OSPF",
        "BGP": "BGP",
        "PIM": "PIM"
    }

    rx_session = re.compile(
        r"^(?P<remote_address>\S+)\s+(?P<state>Up)\s+"
        r"(?P<local_interface>\S+)\s+(?P<detect_time>\d+\.\d+)\s+"
        r"(?P<transmit>\d+\.\d+)\s+(?P<multiplier>\d+)\s*\n"
        r"^\s+Client\s+(?P<client>(?:%s)(?:\s+(?:%s))*).+?\n"
        r".+?"
        r"^\s+Local discriminator (?P<local_discriminator>\d+), "
        r"remote discriminator (?P<remote_discriminator>\d+)" % (
            "|".join(client_map), "|".join(client_map)
        ),
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    def execute(self):
        r = []
        s = self.cli("show bfd session extensive")
        for bs in find_indented(s):
            match = self.rx_session.search(bs)
            if match:
                r += [{
                    # "local_address": IPParameter(),
                    "remote_address": match.group("remote_address"),
                    "local_interface": match.group("local_interface"),
                    "local_discriminator": int(match.group("local_discriminator")),
                    "remote_discriminator": int(match.group("remote_discriminator")),
                    "state": match.group("state").upper(),
                    "clients": [self.client_map[c] for c in match.group("client").split()],
                    # Transmit interval, microseconds
                    "tx_interval": float(match.group("transmit")) * 1000000,
                    "multiplier": int(match.group("multiplier")),
                    # Detection time, microseconds
                    "detect_time": float(match.group("detect_time")) * 1000000
                }]
        return r
