# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Zyxel
# OS:     DSLAM
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zyxel.DSLAM"
    pattern_prompt = r"^(?P<hostname>[a-zA-Z0-9-_\.\s/]+)?>\s*"
    pattern_syntax_error = "((Unknown|invalid) (command|input)|Commands are:)"
    pattern_more = [
        (r"Press any key to continue, 'n' to nopause,'e' to exit", "n"),
        (r"Press any key to continue, 'e' to exit, 'n' for nopause", "n")
    ]
    config_volatile = [r"^time\s+(\d+|date).*?^"]
    command_more = "n"
    command_exit = "exit"

    def convert_interface_name(self, interface):
        if interface.startswith("enet"):
            return "Enet" + interface[4:]
        else:
            return interface

    def setup_session(self, script):
        # Useful only on IES-1000
        script.cli("home", ignore_errors=True)

    rx_slots = re.compile("slot number should between 1 to (?P<slot>\d+)")

    def get_slots_n(self, script):
        try:
            match = self.rx_slots.search(script.cli("lcman show 100", cached=True))
            return int(match.group("slot"))
        except script.CLISyntaxError:
            return 1

    def get_platform(self, script, slot_no, hw):
        if slot_no == 5:
            if hw in ["MSC1000G"]:
                return "IES-5005"
        if slot_no == 6:
            if hw in ["MSC1024GB", "MSC1224GB"]:
                return "IES-5106M"
        if slot_no == 12:
            if hw in ["MSC1024GB", "MSC1224GB"]:
                return "IES-5112M"
        if slot_no == 17:
            if hw in ["MSC1024GB", "MSC1224GB", "MSC1024G", "MSC1224G"]:
                return "IES-6000"
        if (hw == "IES1248-51") and (slot_no == 1):
            return "IES-1248"
        return ""
