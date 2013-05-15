# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Force10
## OS:     SFTOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Force10.SFTOS"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_more = r"^--More-- or \(q\)uit"
    pattern_unpriveleged_prompt = r"^(?P<host>\S+?)>"
    pattern_prompt = r"^(?P<host>\S+?)#"
    pattern_syntax_error = r"% Invalid input detected at "
    pattern_operation_error = r"% Error: "
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "write memory"
    command_submit = "\r"
    convert_interface_name = NOCProfile.convert_interface_name_cisco
