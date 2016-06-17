# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Zyxel
## OS:     MSAN
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zyxel.MSAN"
    pattern_prompt = r"^\S+?>"
    pattern_syntax_error = "invalid (command|input)"
    pattern_more = "Press any key to continue, 'n' to nopause,'e' to exit"
    config_volatile = [r"^time\s+(\d+|date).*?^"]
    command_more = "n"
    command_exit = "exit"

    rx_slots = re.compile("slot number should between 1 to (?P<slot>\d+)")

    def get_slots_n(self, script):
        match = self.rx_slots.search(script.cli("lcman show 100", cached=True))
        return int(match.group("slot"))

    def get_platform(self, script, slot_no, hw):
        if (hw == "MSC1000G") and (slot_no == 5):
            return "IES-5005"
        if (hw == "MSC1024G") and (slot_no == 17):
            return "IES-6000"
        return ""
