# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: Alcatel
# OS:     TIMOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------
import re

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.TIMOS"
    pattern_username = "[Ll]ogin: "
    pattern_password = "[Pp]assword: "
    pattern_prompt = r"^\S+?#"
    pattern_more = r"^Press any key to continue.*$"
    pattern_syntax_error = r"Error: Bad command\.|Error: Invalid parameter\."
    command_disable_pager = "environment no more"
    command_exit = "logout"
    config_volatile = [r"^# Finished.*$", r"^# Generated.*$"]
    command_more = " "
    rogue_chars = [re.compile(r"\r\s+\r"), "\r"]

    def convert_interface_name(self, s):
        if "," in s:
            s = s.split(",", 1)[0].strip()
        return s
