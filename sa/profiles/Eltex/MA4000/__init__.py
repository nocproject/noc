# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     MA4000
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.MA4000"
    pattern_username = r"^\S+ login: "
    pattern_more = [
        (r"\[Yes/press any key for no\]", "Y")
    ]
    pattern_syntax_error = \
        r"^(Command not found. Use '?' to view available commands|" + \
        "Incomplete command\s+|Invalid argument\s+)"
    pattern_prompt = r"^(?P<hostname>\S+)# "
