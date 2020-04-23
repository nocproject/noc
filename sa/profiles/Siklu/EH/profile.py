# ---------------------------------------------------------------------
# Vendor: Siklu
# OS:     EH
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Siklu.EH"
    pattern_username = "[Ll]ogin: "
    pattern_password = "[Pp]assword: "
    pattern_prompt = r"^(?P<hostname>[A-Za-z0-9-_ \:\.\*\'\"\,\(\)\/]+)?>"
    command_submit = "\r"

    rx_strip_cmd_repeat = re.compile(br".+\x1b\[\d+G\r?\n(.*)", re.MULTILINE | re.DOTALL)  # noqa

    def cleaned_input(self, input):
        match = self.rx_strip_cmd_repeat.search(input)
        if match:
            input = match.group(1)
        input = super(Profile, self).cleaned_input(input)
        return input

    def convert_interface_name(self, s):
        if s.lower().startswith("eth"):
            return "eth%s" % s[3:].strip()
        else:
            return s.lower()
