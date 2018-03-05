# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: 3Com
## OS:     4500
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
#from noc.sa.profiles import Profile as NOCProfile
#from noc.sa.models import ManagedObject
from noc.core.profile.base import BaseProfile
import re

class Profile(BaseProfile):
    name = "3Com.4500"
    ##supported_schemes = [BaseProfile.TELNET, BaseProfile.SSH]
    pattern_username = r"^Username:"
    pattern_password = r"^(Password:|Please input password:)"
    pattern_more = [
        (r"^\s+---- More ----$", " "),
        (r"The current configuration will be written to the device. Are you sure? [Y/N]:", "Y"),
        (r"(To leave the existing filename unchanged, press the enter key):", "\n"),
        (r"flash:/startup.cfg exists, overwrite? [Y/N]:", "Y"),
        ]
    pattern_prompt = r"^[<\[]\S+[>\]]"
    pattern_syntax_error = r"^\s+% (Unrecognized|Incomplete) command found at '\^' position.$"
    command_save_config = "save"
    #command_enter_config = "system-view"
    command_leave_config = "return"
    command_exit = "quit"
    convert_interface_name = BaseProfile.convert_interface_name_cisco

    def setup_session(self, script):
        # Yuo may change password instead 512900
	# script.cli("_cmdline-mode on\nY\n512900\nsystem-view\n")
        script.cli("system-view")
        """
        obj = ManagedObject.objects.get()
        passwd = obj.super_password()
        script.cli("_cmdline-mode on\nY\n" + passwd)
        """
