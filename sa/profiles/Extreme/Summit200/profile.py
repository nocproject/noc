# ---------------------------------------------------------------------
# Vendor: Extreme
# OS:     Summit200
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.validators import is_int


class Profile(BaseProfile):
    name = "Extreme.Summit200"

    pattern_prompt = rb"^(?P<hostname>\S+)\:\d+ #"
    pattern_syntax_error = rb"Syntax error at token"
    # command_disable_pager = "disable clipaging"
    pattern_more = rb"Press <SPACE> to continue or <Q> to quit:"
    command_exit = "exit"
    command_more = " "
    config_tokenizer = "line"
    config_tokenizer_settings = {"line_comment": "#"}
    config_volatile = [r"generated \S{3} \S{3} \d+ \d\S+\d \d{4}"]

    @classmethod
    def get_interface_type(cls, name):
        if is_int(name):
            return "physical"
        return "SVI"
