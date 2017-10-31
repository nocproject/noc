# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: 3Com
# OS:     SuperStack3_4500
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "3com.SuperStack3_4500"
    pattern_more = [
        (r"^\s+---- More ----$", " "),
        (r"The current configuration will be written to the device. Are you sure? [Y/N]:", "Y"),
        (r"(To leave the existing filename unchanged, press the enter key):", "\n"),
        (r"flash:/startup.cfg exists, overwrite? [Y/N]:", "Y")
    ]
    pattern_prompt = r"^[<\[]\S+[>\]]"
    pattern_syntax_error = r"\n\s+% (Unrecognized|Incomplete) command found at '\^' position."
    command_save_config = "save"
    command_enter_config = "system-view"
    command_leave_config = "return"
    command_exit = "quit"
    convert_interface_name = BaseProfile.convert_interface_name_cisco
