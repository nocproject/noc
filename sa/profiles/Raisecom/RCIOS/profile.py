# ----------------------------------------------------------------------
# Vendor: Raisecom
# OS:     RCIOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Raisecom.RCIOS"

    pattern_username = rb"^([Uu]ser ?[Nn]ame|[Ll]ogin): ?"
    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)> "
    pattern_super_password = r"^Enable: "
    cli_retries_super_password = 2
    command_super = b"enable"
    pattern_prompt = rb"^(?P<hostname>\S+)# "
    command_exit = "exit"
    pattern_syntax_error = rb"% \".+\"  (?:Unknown command.)"
    pattern_more = [(rb"^--More-- \(\d+% of \d+ bytes\)", b"r")]

    config_tokenizer = "indent"
    config_tokenizer_settings = {
        "line_comment": "!",
    }

    confdb_defaults = [
        ("hints", "system", "user", "defaults", "class", "level-15"),
    ]

    config_normalizer = "RCIOSNormalizer"

    INTERFACE_TYPES = {
        "3g": "tunnel",
        "du": "other",
        "et": "physical",
        "lo": "loopback",
        "sh": "physical",
        "si": "physical",
        "tu": "tunnel",
        "vl": "SVI",
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:2]).lower())
