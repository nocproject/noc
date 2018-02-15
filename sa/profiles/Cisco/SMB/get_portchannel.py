# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.SMB.get_portchannel
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel
from noc.lib.text import split_alnum


class Script(BaseScript):
    name = "Cisco.SMB.get_portchannel"
    interface = IGetPortchannel

    rx_po = re.compile(
        r"^(?P<pcname>Po\d+)\s*(?:Active|Non-candidate): (?P<aports>\S+)?[, ]*(?P<iports>Inactive: \S+)?")

    @staticmethod
    def iter_range(s):
        if "-" not in s:
            yield s
        else:
            first, last = s.rsplit("-", 1)
            parts = split_alnum(first)
            prefix = parts[:-1]
            for i in range(int(parts[-1]), int(last) + 1):
                yield "".join([str(x) for x in prefix + [i]])

    def execute(self):  # TODO: test with real port-channels
        r = []
        s = self.cli("show interfaces Port-Channel", cached=True)
        for l in s.split("\n"):
            match = self.rx_po.match(l.strip())
            if match:
                ports = []
                aports = match.group("aports")
                for p in aports.split(","):
                    ports += list(self.iter_range(p))
                r += [{
                    "interface": match.group("pcname"),
                    "members": ports,  # <!> TODO: inactive ports???
                    "type": "S",  # <!> TODO: port-channel type detection (LACP)
                }]
        return r
