# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Ericsson
## OS:     SEOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Ericsson.SEOS"
    pattern_more = "^---(more)---"
    pattern_unpriveleged_prompt = r"^\S+?>"
    pattern_syntax_error = r"% Invalid input at"
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    pattern_prompt = r"^\[(?P<context>\S+)\](?P<hostname>\S+)#"
