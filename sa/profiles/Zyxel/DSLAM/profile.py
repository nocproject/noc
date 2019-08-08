# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Zyxel
# OS:     DSLAM
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zyxel.DSLAM"
    pattern_prompt = r"^(?P<hostname>[a-zA-Z0-9-_\.\s/]+)?>\s*"
    pattern_syntax_error = "((Unknown|invalid) (command|input)|Commands are:)"
    pattern_more = [
        (r"Press any key to continue, 'n' to nopause,'e' to exit", "n"),
        (r"Press any key to continue, 'e' to exit, 'n' for nopause", "n"),
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
