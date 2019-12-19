# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Juniper
# OS:     SRC-PE
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Juniper.SRCPE"
    pattern_prompt = r"^\S*>"
    pattern_more = r"^ -- MORE -- "
    command_more = " "
    rogue_chars = []
