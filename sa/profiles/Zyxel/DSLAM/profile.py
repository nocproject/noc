# ---------------------------------------------------------------------
# Vendor: Zyxel
# OS:     DSLAM
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zyxel.DSLAM"

    pattern_prompt = rb"^(?P<hostname>[a-zA-Z0-9-_\.\s/]+)?>\s*"
    pattern_syntax_error = rb"((Unknown|invalid) (command|input)|Commands are:)"
    pattern_more = [
        (rb"Press any key to continue, 'n' to nopause,'e' to exit", b"n"),
        (rb"Press any key to continue, 'e' to exit, 'n' for nopause", b"n"),
    ]
    config_volatile = [r"^time\s+(\d+|date).*?^"]
    command_exit = "exit"

    def convert_interface_name(self, interface):
        if interface.startswith("enet"):
            return "Enet" + interface[4:]
        return interface

    def setup_session(self, script):
        # Useful only on IES-1000
        script.cli("home", ignore_errors=True)
