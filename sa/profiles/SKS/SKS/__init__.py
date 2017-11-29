# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: SKS (SVYAZKOMPLEKTSERVICE, LLC. - http://skss.ru/)
# OS:     SKS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "SKS.SKS"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_prompt = r"^(?P<hostname>\S+)\s*(\((config|config-\S+)\)|)\s*#"
    pattern_syntax_error = \
        r"% Unrecognized command|% Wrong number of parameters|% Ambiguous command"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_save_config = "write memory\n"
    command_disable_pager = "terminal datadump"
    command_exit = "exit"
    pattern_more = [
        ("More: <space>,  Quit: q or CTRL+Z, One line: <return>", "a"),
        (r"^\n.+\[Yes/press\s+any\s+key\s+for\s+no\]", "Yes\n")
    ]
