# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_sla_probes
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from itertools import izip
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetslaprobes import IGetSLAProbes


class Script(BaseScript):
    name = "Cisco.IOS.get_sla_probes"
    interface = IGetSLAProbes

    CAP_SLA_SYNTAX = "Cisco | IOS | Syntax | IP SLA"

    SYNTAX_SLA_CONFIG = [
        "show ip sla config",
        "show ip sla monitor config"
    ]

    rx_entry = re.compile(
        r"Entry number: (?P<name>\d+)\s*\n",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    rx_type = re.compile(
        r"Type of operation to perform:\s+(?P<type>\S+)",
        re.MULTILINE | re.IGNORECASE
    )

    rx_target = re.compile(
        "Target address/Source \S+: (?P<target>[^/]+)/",
        re.MULTILINE
    )

    rx_target1 = re.compile(
        "Target address: (?P<target>\S+)",
        re.MULTILINE
    )

    rx_tag = re.compile(
        "Tag: *(?P<tag>[^\n]+)\n",
        re.MULTILINE
    )

    # IOS to interface type conversion
    # @todo: Add other types
    TEST_TYPES = {
        "icmp-echo": "icmp-echo",
        "icmp-jitter": "icmp-echo",
        "echo": "icmp-echo"
    }

    def execute(self, **kwargs):
        if not self.has_capability(self.CAP_SLA_SYNTAX, allow_zero=True):
            return []
        cfg = self.cli(
            self.SYNTAX_SLA_CONFIG[
                self.capabilities[self.CAP_SLA_SYNTAX]
            ]
        )
        r = []
        for name, config in self.iter_pairs(self.rx_entry.split(cfg), offset=1):
            match = self.rx_type.search(config)
            if not match:
                self.logger.error(
                    "Cannot find type for IP SLA probe %s. Ignoring",
                    name
                )
                continue
            type = match.group("type")
            match = self.rx_target.search(config)
            if not match:
                match = self.rx_target1.search(config)
                if not match:
                    self.logger.error(
                        "Cannot find target for IP SLA probe %s. Ignoring",
                        name
                    )
            if type not in self.TEST_TYPES:
                self.logger.error(
                    "Unknown test type %s for IP SLA probe %s. Ignoring",
                    type, name
                )
            type = self.TEST_TYPES[type]
            target = match.group("target")
            r += [{
                "name": name,
                "tests": [{
                    "name": name,
                    "type": type,
                    "target": target
                }]
            }]
            match = self.rx_tag.search(config)
            if match:
                tag = match.group("tag").strip()
                if tag:
                    r[-1]["description"] = tag
        return r
