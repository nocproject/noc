# ---------------------------------------------------------------------
# Vendor: HP
# OS:     Aruba
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.Aruba"

    # INTERFACE_TYPES = {6: "physical", 53: "SVI"}

    pattern_username = rb"Username: ?"
    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+[^#])\s*>\s*"
    pattern_prompt = rb"^(?P<hostname>\S+[^#])\s*?(?:\(config[^\)]*\))?#"
    pattern_syntax_error = rb"(% Ambiguous command.|Cannot execute command.)"
    command_disable_pager = "no page"
    command_super = b"enable"
    pattern_more = [
        (rb"\s--\s*MORE\s*--, next page: Space, next line: Enter, quit: q", b" "),
    ]
    rogue_chars = [re.compile(rb"\r +\r"), b"\r"]
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_exit = "exit"
    config_tokenizer = "indent"
    config_tokenizer_settings = {"line_comment": "!"}
    config_normalizer = "ArubaOSNormalizer"
    # -- MORE --, next page: Space, next line: Enter, quit: q
    # rogue_chars = [
    #     # re.compile(rb"\r\s+\r"),
    #     b"\r",
    #     # re.compile(rb"User \".+\" has logged in \d+ times in the past \d+ days"),
    # ]

    def convert_interface_name(self, s):
        return s

    @classmethod
    def get_interface_type(cls, name):
        name = name.lower()
        if name.startswith("vlan"):
            return "SVI"
        elif name.startswith("lag"):
            return "aggregated"
        return "physical"
