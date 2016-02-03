# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Siklu
## OS:     EH
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Siklu.EH"
    pattern_username = "[Ll]ogin: "
    pattern_password = "[Pp]assword: "
    pattern_prompt = r"^\S+?>"
    command_submit = "\r"

    def cleaned_input(self, input):
        rx_strip_cmd_repeat = re.compile(r'.+\x1b\[\d+G\r?\n(.*)',
            re.MULTILINE | re.DOTALL)
        match = rx_strip_cmd_repeat.search(input)
        if match:
            input = match.group(1)
        input = super(Profile, self).cleaned_input(input)
        return input

    def convert_interface_name(self, s):
        if s.lower().startswith("eth"):
            return "eth%s" % s[3:].strip()
