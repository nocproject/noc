# ---------------------------------------------------------------------
# Vendor: Siklu
# OS:     EH
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Siklu.EH"

    pattern_username = rb"[Ll]ogin: "
    pattern_password = rb"[Pp]assword: "
    pattern_prompt = rb"^(?P<hostname>[A-Za-z0-9-_ \:\.\*\'\"\,\(\)\/]+)?>"
    command_submit = b"\r"

    rx_strip_cmd_repeat = re.compile(rb".+\x1b\[\d+G\r?\n(.*)", re.MULTILINE | re.DOTALL)  # noqa

    def cleaned_input(self, input):
        match = self.rx_strip_cmd_repeat.search(input)
        if match:
            input = match.group(1)
        return super().cleaned_input(input)

    def convert_interface_name(self, s):
        if s.lower().startswith("eth"):
            return "eth%s" % s[3:].strip()
        return s.lower()
