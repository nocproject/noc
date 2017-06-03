# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Alstec
# OS:     MSPU
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alstec.MSPU"
    pattern_prompt = r"^\S+\$> "
    pattern_more = r"^--More-- or \(q\)uit$"
    pattern_syntax_error = r"\^ error"
    command_exit = "exit"
