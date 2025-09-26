# ---------------------------------------------------------------------
# EdgeCore.ES.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_portchannel import Script as BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "EdgeCore.ES.get_portchannel"
    interface = IGetPortchannel
    cache = True

    rx_chan_line_3526 = re.compile(
        r"Information of (?P<interface>Trunk \d+).*?Member Ports(|\s+): (?P<members_str>[^\n]+)",
        re.IGNORECASE | re.DOTALL | re.MULTILINE,
    )
    rx_chan_line_4626 = re.compile(
        r"Port-group number : (?P<number>\d+)", re.IGNORECASE | re.MULTILINE
    )
    rx_memb_line_4626 = re.compile(
        r"\n\d+\s+(?P<member>\S+)\s+(?P<mode>[^\n]+)", re.IGNORECASE | re.DOTALL | re.MULTILINE
    )

    def execute_cli(self):
        if self.is_platform_4626:
            channels = self.cli("show port-group brief")
            r = []
            for match in self.rx_chan_line_4626.finditer(channels):
                details = self.cli("show port-group %s port-channel" % match.group("number"))
                r += [
                    {
                        "interface": "Port-Channel" + match.group("number"),
                        "members": [
                            memb.group("member")
                            for memb in self.rx_memb_line_4626.finditer(details)
                        ],
                        "type": "S",  # <!> TODO: port-channel type detection
                    }
                ]
            return r
        if self.is_platform_3510 or self.is_platform_46 or self.is_platform_ecs4100:
            status = self.cli("show interface status", cached=True)
            r = []
            for match in self.rx_chan_line_3526.finditer(status):
                members = match.group("members_str").strip().rstrip(",").replace("Eth", "Eth ")
                r += [
                    {
                        "interface": match.group("interface"),
                        "members": members.split(", "),
                        "type": "S",
                    }
                ]
            return r
        raise self.NotSupportedError()
