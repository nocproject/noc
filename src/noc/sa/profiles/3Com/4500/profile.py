# ---------------------------------------------------------------------
# Vendor: 3Com
# OS:     4500
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "3Com.4500"
    pattern_username = rb"^Username:"
    pattern_password = rb"^(Password:|Please input password:)"
    pattern_more = [
        (rb"^\s+---- More ----$", b" "),
        (rb"The current configuration will be written to the device. Are you sure? [Y/N]:", b"Y"),
        (rb"(To leave the existing filename unchanged, press the enter key):", b"\n"),
        (rb"flash:/startup.cfg exists, overwrite? [Y/N]:", b"Y"),
    ]
    pattern_prompt = rb"^[<\[]\S+[>\]]"
    pattern_syntax_error = rb"^\s+% (Unrecognized|Incomplete) command found at '\^' position.$"
    command_save_config = "save"
    # command_enter_config = "system-view"
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
