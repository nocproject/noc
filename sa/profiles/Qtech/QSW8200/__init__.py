# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     QSW8200
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Qtech.QSW8200"
    pattern_more = [
        (r"^ --More-- $", " ")
    ]
    pattern_unprivileged_prompt = r"^\S+>"
    pattern_prompt = r"^(?P<hostname>\S+)?#"
    pattern_syntax_error = \
        r"Error input in the position market by|%  Incomplete command"
    # Do not use this. Bogus hardware.
    # command_disable_pager = "terminal page-break disable"
    command_super = "enable"
    command_submit = "\r"
    command_exit = "quit"
