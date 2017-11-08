# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     SMG
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.SMG"
    # pattern_username = r"^\S+ login: "
    # pattern_prompt = r"^(?P<hostname>\S+)# "
    pattern_prompt = r"(SMG2016> )|(/[\w/]+ # )"
    command_exit = "exit"
