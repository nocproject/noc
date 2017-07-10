# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Orion (Orion Networks)
# OS:     NOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Orion.NOS"
    pattern_unpriveleged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = r"^% \" .+ \"  Unknown command."
    command_super = "enable"
    command_disable_pager = "terminal page-break disable"
    pattern_more = " --More-- "
    command_more = " "
    command_exit = "exit"

    rx_ver = re.compile(
        r"^Product name\s*:\s*(?P<platform>.+)\s*\n"
        r"^NOS\s+Version NOS_(?P<version>\d+\.\d+\.\d+).+\n"
        r"(^Support ipv6\s*:\s*(?P<ipv6_support>\S+)\s*\n)?"
        r"^Bootstrap\s+Version (?P<bootprom>(Bootstrap_\d+\.\d+\.\d+|UNKNOWN)).*\n"
        r"^FPGA Version\s*\n"
        r"^Hardware (\S+|\S+\s\S+) Version Rev.(?P<hardware>\S+)\s*\n"
        r"\n"
        r"^System MacAddress is\s*:\s*(?P<mac>\S+)\s*\n"
        r"^Serial number\s*:\s*(?P<serial>\S+)\s*\n",
        re.MULTILINE)

    def get_version(self, script):
        c = script.cli("show version", cached=True)
        return self.rx_ver.search(c).groupdict()
