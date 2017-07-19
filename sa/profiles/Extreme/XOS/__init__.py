# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Extreme
# OS:     XOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Extreme.XOS"
    pattern_prompt = r"^(\*\s)?(Slot-\d+ )?\S+? #"
    pattern_more = "^Press <SPACE> to continue or <Q> to quit:"
    pattern_syntax_error = \
        r"%% (Incomplete command|Invalid input detected at)"
    command_more = " "
    command_disable_pager = "disable clipaging"
