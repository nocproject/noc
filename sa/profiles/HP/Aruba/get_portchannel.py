# ---------------------------------------------------------------------
# HP.Aruba.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.interfaces.igetportchannel import IGetPortchannel
from noc.sa.profiles.Generic.get_portchannel import Script as BaseScript
from noc.core.text import parse_kv


class Script(BaseScript):
    name = "HP.Aruba.get_portchannel"
    interface = IGetPortchannel

    rx_lag_splitter = re.compile(
        r"^Aggregate (?P<lag>lag\d+) is (?P<status>down|up)\s*", re.MULTILINE
    )

    parse_kv_map = {
        "aggregated-interfaces": "port",
        "aggregate mode": "mode",
    }

    def execute_cli(self, **kwargs):
        r = []
        v = self.cli("show lag")
        prev = None
        for match in self.rx_lag_splitter.finditer(v):
            if not prev:
                prev = match
                continue
            ll = parse_kv(self.parse_kv_map, v[prev.start() : match.end()])
            r += [
                {
                    "interface": prev.group("lag"),
                    "members": ll["port"].split(),
                    "type": "L" if ll["mode"] == "active" else "S",
                }
            ]
            prev = match

        return r
