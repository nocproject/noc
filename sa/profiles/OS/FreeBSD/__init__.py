# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: FreeBSD
## OS:     FreeBSD
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "OS.FreeBSD"
    command_super = "su"
    command_exit = "exit"
    pattern_username = r"^[Ll]ogin:"
    pattern_unpriveleged_prompt = r"^\S*?\s*(%|\$)\s*"
    pattern_prompt = r"^(?P<hostname>\S*)\s*#\s*"
    pattern_syntax_error = r": Command not found\."
