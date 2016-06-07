# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Iskratel
## OS:     MSAN
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Iskratel.MSAN"
    pattern_prompt = r"^\S+?>"
    pattern_more = "Press any key to continue or ESC to stop scrolling."
    pattern_syntax_error = r"% Invalid input detected at"
    command_more = " "
    command_exit = "logout"
    command_save_config = "save"
    config_volatile = ["^%.*?$"]
    command_submit = "\r"
    rogue_chars = ["\r\x00"]

    rx_hw = re.compile(
        r"System Description\.+ ISKRATEL Switching\n"
        r"Current CPU Load\.+ \d+%\n"
        r"Board Type\.+ (?P<platform>\S+)\n"
        r"Burned In MAC Address\.+ (?P<mac>\S+)\n"
        r"Board Serial Number\.+ (?P<serial>\S+)\n"
        r"Board Part Number\.+ (?P<part_no>\S+)\n"
        r"My board Position\.+ \d+\n"
        r"IPMI version\.+ (?P<ipmi_ver>\S+)\n"
        r"Puma API Version\.+ (?P<api_ver>\S+)\n"
        r"Puma Microcode Version\.+ (?P<micr_ver>\S+)\n",
        re.MULTILINE)

    def get_hardware(self, script):
        c = script.cli("show hardware", cached=True)
        return self.rx_hw.search(c).groupdict()
