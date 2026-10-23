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

    pattern_prompt = rb"^\S*>"
    pattern_more = [(rb"^ -- MORE -- ", b" ")]
    rogue_chars = []
