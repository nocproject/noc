# ---------------------------------------------------------------------
# Vendor: NAG
# OS:     SNR
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NAG.SNR"
    pattern_more = [
        (r"^ --More-- ", "\n"),
        (r"^Confirm to overwrite current startup-config configuration \[Y/N\]:", "y\n"),
    ]
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"
    # command_disable_pager = "terminal length 200"
    command_exit = "exit"
    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "!"}

    rx_pager = re.compile(r"0 for no pausing")

    def setup_session(self, script):
        # For old models
        script.cli("terminal length 200", ignore_errors=True)
        # For new models
        c = script.cli("terminal length ?", command_submit=b"", ignore_errors=True)
        match = self.rx_pager.search(c)
        if match:
            script.cli("\x01\x0bterminal length 0", ignore_errors=True)

    INTERFACE_TYPES = {
        "Ethe": "physical",  # Ethernet
        "Vlan": "SVI",  # Vlan
        "Port": "aggregated",  # Port-Channel
        "Vsf-": "aggregated",  # Vsf-Port
        "vpls": "unknown",  # vpls_dev
        "l2ov": "tunnel",  # l2overgre
    }

    @classmethod
    def get_interface_type(cls, name):
        if name == "Ethernet0":
            return "management"
        return cls.INTERFACE_TYPES.get(name[:4])
