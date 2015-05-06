# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Brocade
## OS:     CER
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = 'Brocade.CER'
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_more = '--More--'
    pattern_prompt = '\\S+?(\\(\\S+\\))?#'
    pattern_unpriveleged_prompt = '^\\S+?>'
    pattern_syntax_error = 'Invalid input ->|Ambiguous input ->|Incomplete command.'
    pattern_username = 'Login'
    username_submit = '\r'
    password_submit = '\r'
    command_disable_pager = 'skip-page-display'
    command_enter_config = 'configure terminal'
    command_leave_config = 'end'
    command_save_config = 'write memory'
    command_super = 'enable'
    command_exit = 'exit/rexit'
    command_submit = '\r'
    command_more = ' '
    pattern_prompt = '^\\S*@(?P<hostname>[a-zA-Z0-9]\\S*?)(?:-\\d+)?(?:\\(config[^\\)]*\\))?#'
