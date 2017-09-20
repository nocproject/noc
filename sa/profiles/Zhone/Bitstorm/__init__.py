# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Zhone
# OS:     Bitstorm
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zhone.Bitstorm"
    # pattern_unprivileged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_username = r"Login>"
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"
    command_disable_pager = "paging disable"
    pattern_password = r"Password>"
    # pattern_prompt = r"^(?P<hostname>\S+)\s*[#>]"
    # pattern_prompt = r"^(?P<hostname>\S+)(?<!Login)(?<!Password)\s*[#>]"
    pattern_prompt = \
        r"^[\s\*]*(?P<hostname>[\S\s]+)(?<!Login)(?<!Password)\s*(\(\S+\)){0,4}(]|)[#>]"
    pattern_syntax_error = r"ERROR: Permission denied."
    pattern_more = \
        "<SPACE> for next page, <CR> for next line, A for all, Q to quit"
    command_more = "a"
    command_exit = "exit"
