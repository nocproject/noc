# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOS.get_sla_probes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetslaprobes import IGetSLAProbes


class Script(BaseScript):
    name = "Juniper.JUNOS.get_sla_probes"
    interface = IGetSLAProbes

    rx_res = re.compile(
        r"^\s+Owner: (?P<owner>\S+), Test: (?P<test>\S+)\s*\n"
        r"^\s+Target address: (?P<target>\S+), Probe type: (?P<type>\S+)(,|\n)"
        r"(^\s+Routing Instance Name: \S+\s*\n)?"
        r"\s+Test size: \d+ probes\s*\n"
        r"^\s+Probe results:\s*\n"
        r"^\s+Response received,.+,(?P<hw_timestamp>.+)\n",
        re.MULTILINE,
    )

    TEST_TYPES = {
        "icmp-ping": "icmp-echo",
        "icmp-ping-timestamp": "icmp-echo",
        "icmp6-ping": "icmp-echo",
        "udp-ping": "udp-echo",
        "http-get": "http-get",
    }

    def execute_cli(self):
        r = []
        v = self.cli("show services rpm probe-results")
        for match in self.rx_res.finditer(v):
            r += [
                {
                    "group": match.group("owner"),
                    "name": match.group("test"),
                    "type": self.TEST_TYPES[match.group("type")],
                    "target": match.group("target"),
                    "hw_timestamp": match.group("hw_timestamp").strip() != "No hardware timestamps",
                }
            ]
        return r
