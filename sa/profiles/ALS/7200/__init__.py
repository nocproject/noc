# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: ALS
## OS:     7200
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ALS.7200"
    pattern_username = r"^User:"
    pattern_unpriveleged_prompt = r"^\S+ >"
    pattern_prompt = r"^\S+ #"
    pattern_more = r"^--More-- or \(q\)uit$"
    pattern_syntax_error = r"^(% Invalid input detected at|Command not found)"
    command_super = "enable"
    #command_submit = "\r"
    command_exit = "exit\nexit"
