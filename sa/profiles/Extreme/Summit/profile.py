# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Extreme
# OS:     Summit
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Extreme.Summit"
    pattern_prompt = r"^\*(?P<hostname>.+)\:\d+ #"
    pattern_syntax_error = r"Syntax error at token"
    # command_disable_pager = "disable clipaging"
    command_exit = "exit"
    config_tokenizer = "line"
    config_tokenizer_settings = {
        "line_comment": "#"
    }
    config_volatile = [r"generated \S{3} \S{3} \d+ \d\S+\d \d{4}"]
