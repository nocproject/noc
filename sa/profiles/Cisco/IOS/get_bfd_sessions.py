# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_bfd_sessions
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetbfdsessions import IGetBFDSessions

class Script(NOCScript):
    name = "Cisco.IOS.get_bfd_sessions"
    implements = [IGetBFDSessions]

    rx_session_sep = re.compile(
        r"^OurAddr\s+NeighAddr\s+LD/RD\s+RH/RS\s+Holdown\(mult\)\s+State\s+Int\n",
        re.MULTILINE | re.IGNORECASE)

    rx_session = re.compile(
        r"(?P<local_address>\S+)\s+"
        r"(?P<remote_address>\S+)\s+"
        r".+?\s+"
        r"(?P<holdown>\d+)\s*\((?P<mult>\d+)\s*\)\s+"
        r"(?P<state>\S+)\s+"
        r"(?P<local_interface>.+?)\s+\n"
        r"Session.+?"
        r"MinTxInt:\s+(?P<tx_interval>\d+).+"
        r"Registered\sprotocols:\s(?P<protocols>.+)\n"
        r"Uptime.+"
        r"My\sDiscr\.:\s(?P<local_discriminator>\d+)\s+-\s"
        r"Your\sDiscr\.:\s(?P<remote_discriminator>\d+)\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE)

    rx_nl = re.compile("\n+", re.MULTILINE)

    # IOS to interface client type mappings
    client_map = {
        "ISIS": "ISIS",
        "OSPF": "OSPF",
        "BGP": "BGP",
        "EIGRP": "EIGRP"
    }

    def execute(self):
        r = []
        s = self.cli("show bfd neighbors details")
        s = self.rx_nl.sub("\n", s)
        for ss in self.rx_session_sep.split(s)[1:]:
            match = self.re_search(self.rx_session, ss)
            r += [{
                "remote_address": match.group("remote_address"),
                "local_interface": match.group("local_interface"),
                "local_discriminator": int(match.group("local_discriminator")),
                "remote_discriminator": int(match.group("remote_discriminator")),
                "state": match.group("state").upper(),
                "clients": [self.client_map[c] for c in match.group("protocols").split()],
                "tx_interval": int(match.group("tx_interval")),
                "multiplier": int(match.group("mult")),
                "detect_time": int(match.group("holdown")) * 1000
            }]
        return r
