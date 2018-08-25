# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOS.get_bfd_sessions
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetbfdsessions import IGetBFDSessions


class Script(BaseScript):
    name = "Cisco.IOS.get_bfd_sessions"
    interface = IGetBFDSessions

    rx_session_sep = re.compile(
        r"^OurAddr\s+NeighAddr\s+LD/RD\s+RH/RS\s+Holdown\(mult\)\s+State\s+Int\n",
        re.MULTILINE | re.IGNORECASE)

    rx_session_sep2 = re.compile(
        r"^NeighAddr\s+LD/RD\s+RH/RS\s+State\s+Int\n",
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

    rx_session2 = re.compile(
        r"(?P<remote_address>\S+)\s+"
        r"(?P<local_discriminator>\d+)/(?P<remote_discriminator>\d+)\s+"
        r"(?P<rh_state>\S+)\s+(?P<state>\S+)\s+"
        r"(?P<local_interface>.+?)\s*\n.+"
        r"OurAddr:\s+(?P<local_address>\S+)\s.+"
        r"MinTxInt:\s+(?P<tx_interval>\d+).+"
        r"Multiplier:\s+(?P<mult>\d+).+"
        r"Holddown\s\(hits\):\s+(?P<holdown>\d+)\s*\(.+"
        r"Registered\sprotocols:\s(?P<protocols>.+?)\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    rx_nl = re.compile("\n+", re.MULTILINE)

    # IOS to interface client type mappings
    client_map = {
        "ISIS": "ISIS",
        "OSPF": "OSPF",
        "BGP": "BGP",
        "EIGRP": "EIGRP"
    }

    client_ignored = ["CEF"]

    def execute(self):
        r = []
        try:
            s = self.cli("show bfd neighbors details")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        s = self.rx_nl.sub("\n", s)
        # if self.rx_session_sep2.match(s):
        if "IPv4 Sessions" in s:
            splitter = self.rx_session_sep2
            matcher = self.rx_session2
        else:
            splitter = self.rx_session_sep
            matcher = self.rx_session
        for ss in splitter.split(s)[1:]:
            if not ss:
                continue
            match = self.re_search(matcher, ss)
            r += [{
                "remote_address": match.group("remote_address"),
                "local_interface": match.group("local_interface"),
                "local_discriminator": int(match.group("local_discriminator")),
                "remote_discriminator": int(match.group("remote_discriminator")),
                "state": match.group("state").upper(),
                "clients": [self.client_map[c] for c in match.group("protocols").split()
                            if c not in self.client_ignored],
                "tx_interval": int(match.group("tx_interval")),
                "multiplier": int(match.group("mult")),
                "detect_time": int(match.group("holdown")) * 1000
            }]
        return r
