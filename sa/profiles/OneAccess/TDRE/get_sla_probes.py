# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OneAccess.TDRE.get_sla_probes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetslaprobes import IGetSLAProbes


class Script(BaseScript):
    name = "OneAccess.TDRE.get_sla_probes"
    interface = IGetSLAProbes

    rx_probe = re.compile(
        r"^\s+name = (?P<name>\S+)\s*\n"
        r"^\s+adminStatus = enabled\s*\n"
        r"^\s+ipAddress = (?P<target>\S+)\s*\n"
        r"^\s+hostName = .+\n"
        r"^\s+source = .+\n"
        r"^\s+tos = \d+\s*\n"
        r"^\s+priority = .+\n"
        r"^\s+protocol = \s*\n"
        r"^\s+{*\n"
        r"^\s+(?P<type>\S+) .+\n"
        r"^\s+}*\n",
        re.MULTILINE
    )

    TEST_TYPES = {
        "icmp": "icmp-echo",
        "udpEcho": "udp-echo"
    }

    def execute(self):
        r = []
        c = self.cli("SELGRP \"Edit Configuration\"")
        c = self.cli("GET ip/router/qualityMonitor/destinations[]")
        for match in self.rx_probe.finditer(c):
            test = {
                "name": match.group("name"),
                "type": self.TEST_TYPES[match.group("type")],
                "target": match.group("target"),
            }
            r += [{"name": match.group("name"), "tests": [test]}]
        return r
