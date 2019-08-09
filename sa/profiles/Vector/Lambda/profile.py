# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: Vector
# OS:     Lambda
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Vector.Lambda"
    pattern_username = r"^ login: "
    pattern_password = r"^ password: "
    pattern_prompt = r"^>"
    command_exit = "logout"
    pattern_syntax_error = r"invalid command: .*"
