# ---------------------------------------------------------------------
# Vendor: Alstec
# OS:     MSPU
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alstec.MSPU"

    pattern_prompt = rb"^\S+\s*\$> "
    pattern_more = [(rb"^--More-- or \(q\)uit$", b"\n")]
    pattern_syntax_error = rb"\^ error"
    command_exit = "exit"

    INTERFACE_TYPES = {
        "ad": "physical",  # adsl
        "up": "physical",  # uplink
        "et": "physical",  # eth
        "lo": "loopback",
        "br": "SVI",  # brUIK
        "hb": "SVI",  # hbr
        "he": "SVI",  # heoa
        "hu": "SVI",  # huplink
        "hd": "physical",  # hdlc1
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2].lower())
