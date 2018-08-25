# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.XOS.get_portchannel
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python module
import re
# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetportchannel import IGetPortchannel


class Script(BaseScript):
    name = "Extreme.XOS.get_portchannel"
    interface = IGetPortchannel
    rx_trunk = re.compile(r"Group ID\s+:\s+(?P<trunk>\d+).+?Type\s+:\s+(?P<type>\S+).+?Member Port\s+:\s+(?P<members>\S+).+?Status\s+:\s+(?P<status>\S+)", re.MULTILINE | re.DOTALL)
    rx_sh_master = re.compile(r"^\s+(?P<trunk>\d+)+\s+(\d+\s+)?(?P<type>\S+)\s+\S+\s+(?P<member>\d+)\s+\S\s+(?P<status>\S).+", re.IGNORECASE | re.DOTALL)
    rx_sh_member = re.compile(r"^\s+Members:\s+(?P<members>\S+).+", re.IGNORECASE | re.DOTALL)

    def execute_cli(self):
        try:
            t = self.cli("show sharing")
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        r = []
        if "Load Sharing Monitor" in t:
            # @todo LAG name is same on interface name
            """
            Load Sharing Monitor
            Config    Current Agg     Min    Ld Share  Flags Ld Share  Agg Link  Link Up
            Master    Master  Control Active Algorithm       Group     Mbr State Transitions
            ================================================================================
              1:47            LACP       1    L3_L4     A     1:47      -     R       0
                                              L3_L4           1:48      -     R       0
              1:49   1:49     LACP       1    L3_L4     A     1:49      Y     A       2
                                              L3_L4           2:49      Y     A       3
            ================================================================================
            """
            for d in self.profile.parse_table_struct(t, header_start="Config", table_start="=======",
                                                     table_end="======="):
                r += [{
                    "interface": "T%s" % d["Config Master"][0],
                    "members": d["Ld Share Group"],
                    "type": "L" if d["Agg Control"][0].lower() == "lacp" else "S"
                }]
        else:
            for tt in t.strip().split("\n"):
                match = self.rx_sh_master.search(tt)
                if match:
                    try:
                        mem = self.cli("show port %s information detail | include Members" % match.group("trunk"))
                    except self.CLISyntaxError:
                        raise self.NotSupportedError()
                    memmatch = self.rx_sh_member.search(mem)
                    if memmatch:
                        tr_members = self.expand_interface_range(memmatch.group("members"))
                    else:
                        tr_members = self.expand_interface_range(match.group("member"))
                    r += [{
                        "interface": "T%s" % match.group("trunk"),
                        "members": tr_members,
                        "type": "L" if match.group("type").lower() == "lacp" else "S"
                    }]
        return r
