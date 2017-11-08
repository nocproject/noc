# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Rubytech
# OS:     l2ms
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
'''
'''

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Rubytech.l2ms"
    pattern_more = [
        (r"^Error1:", "\n"),
    ]
    command_leave_config = "end"
    command_exit = "exit"
    command_save_config = "save start\n"
    pattern_prompt = \
        r"^(?P<hostname>[a-zA-Z0-9]\S{0,19})(?:[-_\d\w]+)?" \
        r"(?:\(config[^\)]*\)|\(system\))?#\s"
