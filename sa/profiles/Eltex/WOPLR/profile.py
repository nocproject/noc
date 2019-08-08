# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     WOPLR
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.WOPLR"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#|~ #"
    command_exit = "exit"
    pattern_syntax_error = r"Invalid command\."
