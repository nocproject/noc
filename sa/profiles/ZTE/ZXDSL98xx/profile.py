# ---------------------------------------------------------------------
# Vendor: ZTE
# OS:     ZXDSL98xx
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ZTE.ZXDSL98xx"

    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+>)"
    pattern_prompt = rb"^(?!#)\S+[$#] "
    pattern_syntax_error = rb"Error: (%Invalid parameter|Bad command)"
    pattern_operation_error = rb"Error: Too many user login..."
    pattern_more = [(rb"\nPress any key to continue \(Q to quit\)", b" ")]
    # Are you sure to quit? yes[Y] or no[N]
    command_super = b"enable"
    rogue_chars = [re.compile(rb"^\s{10,}\r"), b"\r"]
    config_volatile = ["<entry1 sessionID=.+?/>"]
    username_submit = b"\r"
    password_submit = b"\r"
    command_submit = b"\r"
    command_exit = "logout"
    telnet_send_on_connect = b"\n"

    matchers = {"is_9806h": {"platform": {"$regex": "9806H"}}}

    rx_card = re.compile(
        r"\s+(?P<slot>\d+)\s+(?P<cfgtype>\S+)\s+(?P<port>\d+)\s+"
        r"(?P<hardver>V?\S+|)\s+(?P<softver>V\S+|)\s+(?P<status>Inservice|Offline)\s+"
        r"(?P<serial>\S+)"
    )

    def fill_ports(self, script):
        r = []
        v = script.cli("show card")
        for line in v.splitlines():
            match = self.rx_card.search(line)
            if match:
                r += [match.groupdict()]
        return r
