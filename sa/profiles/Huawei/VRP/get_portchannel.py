# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
from noc.sa.profiles.Generic.get_portchannel import Script as BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "Huawei.VRP.get_portchannel"
    interface = IGetPortchannel
    cache = True

    rx_chan_line_vrp5 = re.compile(
        r"(?P<interface>Eth-Trunk\d+).*?\n"
        r"(?:LAG ID: \d+\s+)?Working\s?Mode: (?P<mode>\S+).*?\n"
        r"(?:Actor)?PortName[^\n]+(?P<members>.*?)(\n\s*\n|\n\s\s)",
        re.IGNORECASE | re.DOTALL | re.MULTILINE,
    )

    def execute_cli(self):
        if self.is_kernel_3:
            self.logger.info("Huawei 3.XX not portchannel command")
            return []
        r = []
        try:
            trunk = self.cli("display eth-trunk", cached=True)
        except self.CLISyntaxError:
            try:
                trunk = self.cli("display link-aggregation summary", cached=True)
            except self.CLISyntaxError:
                return []
            """
            Need more examples

            version 5.2 produce like this:
            No link-aggregation group defined at present.
            version 5.3 produce like this:
            Error: No valid trunk in the system.
            """
            return []
        for match in self.rx_chan_line_vrp5.finditer(trunk):
            r += [
                {
                    "interface": match.group("interface"),
                    "members": [
                        l.split(" ", 1)[0] for l in match.group("members").lstrip("\n").splitlines()
                    ],
                    "type": {"normal": "S", "static": "L", "lacp": "L", "dynamic": "L"}[
                        match.group("mode").lower()
                    ],
                }
            ]
        return r
