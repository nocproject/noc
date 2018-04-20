# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: DLink
# OS:     DVG
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DLink.DVG"
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    submit_command = "\r"
    username_submit = "\n\r"
    password_submit = "\r\n"
    pattern_username = r"^(User: |\S+ login: )"
<<<<<<< HEAD
=======
    pattern_password = r"^Password:"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
