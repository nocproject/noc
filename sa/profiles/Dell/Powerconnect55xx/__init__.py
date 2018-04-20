# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Dell
# OS:     Powerconnect55xx
# Compatible:
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Dell.Powerconnect55xx"
    pattern_username = "[Uu]ser( [Nn]ame)?:"
    pattern_more = "^More: \<space\>"
    pattern_unprivileged_prompt = r"^\S+>"
=======
##----------------------------------------------------------------------
## Vendor: Dell
## OS:     Powerconnect55xx
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
    name = "Dell.Powerconnect55xx"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_username = "[Uu]ser( [Nn]ame)?:"
    pattern_password = "[Pp]ass[Ww]ord:"
    pattern_more = "^More: \<space\>"
    pattern_unpriveleged_prompt = r"^\S+>"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_syntax_error = r"% (?:Unrecognized|Incomplete) command"
    pattern_prompt = r"^(?P<hostname>\S+(:\S+)*)#"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_more = " "
    command_exit = "exit"
    command_save_config = "write"
    config_volatile = ["^%.*?$"]

    def convert_interface_name(self, interface):
        if interface.lower().startswith("vlan "):
            return "vlan" + interface[6:]
        else:
            return interface
