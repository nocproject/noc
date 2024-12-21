# ---------------------------------------------------------------------
# Vendor: NAG
# OS:     SNR
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NAG.SNR"
    pattern_prompt = rb"^(?P<hostname>\S+)(?:\(config[^\)]*\))?[#>]"
    pattern_more = [
        (rb"^ --More-- ", b"\n"),
        (
            rb"^Confirm to overwrite (?:current startup-config configuration|the existed destination file\?)\s+\[Y/N\]:",
            b"y\n",
        ),
        (rb"^\.\.\.\.press ENTER to next line, Q to quit, other key to next page\.\.\.\.", b" "),
    ]
    pattern_syntax_error = (
        rb"% (?:Unrecognized|Incomplete) command, and error detected at"
        rb"|Incomplete command|Too many parameters"
    )
    username_submit = b"\r"
    password_submit = b"\r"
    command_submit = b"\r"
    # command_disable_pager = "terminal length 200"
    command_super = b"enable"
    command_exit = "exit"
    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "!"}
    matchers = {"is_foxgate_cli": {"caps": {"$in": ["NAG | SNR | CLI | Old"]}}}

    rx_pager = re.compile(r"0 for no pausing")

    def setup_session(self, script):
        # For old models
        script.cli("terminal length 200", ignore_errors=True)
        # For new models
        c = script.cli("terminal length ?", command_submit=b"", ignore_errors=True)
        match = self.rx_pager.search(c)
        if match:
            script.cli("\x01\x0bterminal length 0", ignore_errors=True)
        elif "% Unrecognized command" in c:  # Return to normal prompt
            script.cli("", ignore_errors=True)

    INTERFACE_TYPES = {
        "Ethe": "physical",  # Ethernet
        "Vlan": "SVI",  # Vlan
        "syst": "SVI",  # system
        "Port": "aggregated",  # Port-Channel
        "Vsf-": "aggregated",  # Vsf-Port
        "vpls": "unknown",  # vpls_dev
        "l2ov": "tunnel",  # l2overgre
    }

    @classmethod
    def get_interface_type(cls, name):
        if name == "Ethernet0":
            return "management"
        if name.startswith("e0/"):
            return "physical"
        return cls.INTERFACE_TYPES.get(name[:4])
