# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: DCN
# OS:     DCWL
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
'''
'''
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DCN.DCWL"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    command_more = "\n"
    command_submit = "\n"
    command_exit = "exit"
