# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: 3Com
## OS:     SuperStack3
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

import re
## NOC modules
from noc.core.profile.base import BaseProfile
from noc.lib.validators import is_int


class Profile(BaseProfile):
    name = "3Com.SuperStack3"
    pattern_prompt = r"^Select menu option.*:"
    pattern_more = [
        (r"Enter <CR> for more or 'q' to quit--:", "\r"),
    ]
    command_submit = "\r"
    username_submit = "\r"
    password_submit = "\r"
    command_exit = "logout"
    telnet_send_on_connect = "\r"
    convert_mac = BaseProfile.convert_mac_to_dashed

    def get_interface_names(self, name):
        r = []
        if name.startswith("1:"):
            r += [name[2:]]
        else:
            if is_int(name):
                r += ["1:%s" % name]
        return r

    def convert_interface_name(self, name):
        if is_int(name) and (not name.startswith("1:")):
            return "1:" + name
        return name

    rx_hw = re.compile(
        r"^3Com (?P<platform>.+)\n"
        r"(\n)?"
        r"^System Name\s*:.+\n"
        r"^Location\s*:.+\n"
        r"^Contact\s*:.+\n"
        r"\n"
        r"^Time since reset\s*:.+\n"
        r"^Operational Version\s*:\s*(?P<version>\S+)\s*\n"
        r"^Hardware Version\s*:\s*(?P<hardware>\S+)\s*\n"
        r"^Boot Version\s*:\s*(?P<bootprom>\S+)\s*\n"
        r"^MAC address\s*:\s*(?P<mac>\S+)\s*\n"
        r"^Product Number\s*:\s*(?P<part_no>\S+)\s*\n"
        r"^Serial Number\s*:\s*(?P<serial>\S+)\s*\n",
        re.MULTILINE | re.IGNORECASE)

    def get_hardware(self, script):
        c = script.cli("system summary", cached=True)
        return self.rx_hw.search(c).groupdict()
