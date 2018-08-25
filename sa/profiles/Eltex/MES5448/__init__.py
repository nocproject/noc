# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     MES6448
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.MES5448"
    pattern_more = [
        (r"--More-- or \(q\)uit", " ")
    ]
    #pattern_unprivileged_prompt = r"^(?P<hostname>\S+)>"
    pattern_prompt = r"^(?P<hostname>\S+)#"
    pattern_syntax_error = \
        r"^% (Unrecognized command|Incomplete command|" \
        r"Wrong number of parameters or invalid range, size or " \
        r"characters entered)$"
    command_disable_pager = "terminal length 0"

