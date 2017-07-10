# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Brocade
# OS:     ADX
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = 'Brocade.ADX'
    pattern_more = '--More--'
    pattern_unpriveleged_prompt = \
        r"^\S+@(?P<hostname>[a-zA-Z0-9]\S{0,19})(?:[-_\d\w]+)?" \
        r"(?:\(conf[^\)]*\))?>"
    pattern_prompt = \
        r"^\S*@(?P<hostname>[a-zA-Z0-9]\S*?)(?:-\d+)?(?:\(config[^\)]*\))?#"
    pattern_syntax_error = \
        'Invalid input ->|Ambiguous input ->|Incomplete command.'
    command_super = "enable"
    command_disable_pager = "terminal length 0"
    command_enter_config = 'configure terminal'
    command_leave_config = 'end'
    command_save_config = 'write memory'
    command_exit = 'exit/rexit'
    command_submit = '\r'
    command_more = ' '
