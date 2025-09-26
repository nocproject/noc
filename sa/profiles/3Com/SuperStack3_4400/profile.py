# ----------------------------------------------------------------------
# Vendor: 3Com
# OS:     SuperStack3_4400
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import re

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.validators import is_int


class Profile(BaseProfile):
    name = "3Com.SuperStack3_4400"
    pattern_prompt = rb"^Select menu option.*:"
    pattern_more = [(rb"(|-- )Enter <CR> for more or 'q' to quit(--|\s--):", b"\r\n")]
    command_submit = b"\r\n"
    username_submit = b"\r\n"
    password_submit = b"\r\n"
    command_exit = "logout"
    convert_mac = BaseProfile.convert_mac_to_dashed

    def get_interface_names(self, name):
        r = []
        if name.startswith("1:"):
            r += [name[2:]]
        elif is_int(name):
            r += ["1:%s" % name]
        return r

    def convert_interface_name(self, name):
        if is_int(name) and (not name.startswith("1:")):
            return "1:" + name
        return name

    rx_hw = re.compile(
        r"^3Com (?P<platform>.+)\n"
        r"^System Name\t+:.+\n"
        r"^Location\s*:.+\n"
        r"^Contact\s*:.+\n"
        r"\n"
        r"^Time Since Reset\s*:.+\n"
        r"^Operational Version\t+:\s+(?P<version>\S+)\n"
        r"^Hardware Version\t+:\s+(?P<hardware>\S+)\n"
        r"^Boot Version\t+:\s+(?P<bootprom>\S+)\n"
        r"^MAC Address\t+:\s+(?P<mac>\S+)\n"
        r"^Product Number\t*:\s+(?P<part_no>\S+)\n"
        r"^Serial Number\t*:\s+(?P<serial>\S+)\n",
        re.MULTILINE | re.IGNORECASE,
    )

    def get_hardware(self, script):
        c = script.cli("system summary", cached=True)
        return self.rx_hw.search(c).groupdict()
