# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Dell
## OS:     Powerconnect
## Compatible:
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Dell.Powerconnect"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_username = "[Uu]ser:"
    pattern_password = "[Pp]ass[Ww]ord:"
    pattern_more = "--More--"
    pattern_unpriveleged_prompt = r"^\S+>"
    pattern_syntax_error = r"% Invalid input detected at"
    command_super = "enable"
    pattern_prompt = r"^(?P<hostname>\S+(:\S+)*)#"
    command_more = " "
    command_exit = "logout"
    command_save_config = "copy running-config startup-config"
    config_volatile = ["^%.*?$"]
