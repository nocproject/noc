# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: D-Link
## OS:     DFL
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "DLink.DFL"
    pattern_username = "([Uu]ser ?[Nn]ame|[Ll]ogin):"
    pattern_password = "[Pp]ass[Ww]ord:"
    pattern_syntax_error = r"Error: Unknown command:"
    pattern_prompt = r"^(?P<hostname>\S+(:\S+)*):/> "
    command_more = "a"
    command_exit = "logout"
    config_volatile = ["^%.*?$"]
