# -*- coding: utf-8 -*-
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
    pattern_prompt = r"^\S+\$> "
    pattern_more = r"^--More-- or \(q\)uit$"
    pattern_syntax_error = r"\^ error"
    command_exit = "exit"

    INTERFACE_TYPES = {
        "ad": "physical",  # adsl
        "up": "physical",  # uplink
        "lo": "loopback",
        "br": "SVI",  # brUIK
        "hb": "SVI",  # hbr
        "he": "SVI",  # heoa
        "hu": "SVI",  # huplink
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2].lower())
