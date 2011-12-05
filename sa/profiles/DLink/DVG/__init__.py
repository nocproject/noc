# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: DLink
## OS:     DVG
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "DLink.DVG"
    supported_schemes = [NOCProfile.TELNET]
    submit_command = "\r"
    username_submit = "\n\r"
    password_submit = "\r\n"
    pattern_username = r"^(User: |\S+ login: )"
    pattern_password = r"^Password:"
    pattern_more = [
        (r"^Disconnect Now? (Y/N)", "Y"),
        (r"^More: <space>,  Quit: q, One line: <return>$", " ")
    ]
    pattern_syntax_error = r"^\s+\^\s+(\[Command Not Found\]|Option Not Found)$"
    command_enter_config = "CD /"
    command_leave_config = "SUBMIT"
    command_save_config = "SAVE"
    pattern_prompt = r"^> "
    command_exit = "BYE"
