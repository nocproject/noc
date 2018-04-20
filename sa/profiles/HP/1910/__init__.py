# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: HP, 3Com
# OS:     1910, BaseLine
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile
# from noc.sa.models import ManagedObject


class Profile(BaseProfile):
    name = "HP.1910"
=======
##----------------------------------------------------------------------
## Vendor: HP, 3Com
## OS:     1910, BaseLine
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles import Profile as NOCProfile
#from noc.sa.models import ManagedObject

class Profile(NOCProfile):
    name = "HP.1910"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_username = r"^Username:"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_password = r"^(Password:|Please input password:)"
    pattern_more = [
        (r"^\s+---- More ----$", " "),
        (r"The current configuration will be written to the device. Are you sure? [Y/N]:", "Y"),
        (r"(To leave the existing filename unchanged, press the enter key):", "\n"),
<<<<<<< HEAD
        (r"flash:/startup.cfg exists, overwrite? [Y/N]:", "Y")
    ]
    pattern_prompt = r"^[<\[]\S+[>\]]"
    pattern_syntax_error = \
        r"^\s+% (Unrecognized|Incomplete) command found at '\^' position.$"
=======
        (r"flash:/startup.cfg exists, overwrite? [Y/N]:", "Y"),
        ]
    pattern_prompt = r"^[<\[]\S+[>\]]"
    pattern_syntax_error = r"^\s+% (Unrecognized|Incomplete) command found at '\^' position.$"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    command_save_config = "save"
    command_enter_config = "system-view"
    command_leave_config = "return"
    command_exit = "quit"
<<<<<<< HEAD
    convert_interface_name = BaseProfile.convert_interface_name_cisco

    def setup_session(self, script):
        # Yuo may change password instead 512900
        # script.cli("_cmdline-mode on\nY\n512900\nsystem-view\n")
=======
    convert_interface_name = NOCProfile.convert_interface_name_cisco

    def setup_session(self, script):
        # Yuo may change password instead 512900
#        script.cli("_cmdline-mode on\nY\n512900\nsystem-view\n")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        script.cli("_cmdline-mode on\nY\n512900")
        """
        obj = ManagedObject.objects.get()
        passwd = obj.super_password()
        script.cli("_cmdline-mode on\nY\n" + passwd)
        """
