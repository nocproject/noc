# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     RG
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.RG"
    pattern_username = "^\S+ [Ll]ogin:"
    pattern_password = "^[Pp]assword:"
    pattern_prompt = r"^\S+\$ "
    command_exit = "exit"
    command_more = "\n"

    PLATFORMS = {
        "46": "RG-1404GF-W"
    }

    @classmethod
    def get_platforms(cls, name):
        return cls.PLATFORMS.get(name)
