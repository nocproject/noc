# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Huawei
# OS:     MA5300
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Huawei.MA5300"
    pattern_more = [
        (r"--- More:", " "),
        (r"---- More \(Press CTRL\+C break\) ---", " "),
        (r"Note: Terminal", "\n"),
        (r"Warning: Battery is low power!", "\n"),
        (r"\{\s<cr>.*\s\}:", "\n"),
        (r"^Are you sure?\[Y/N\]", "y\n")
    ]
    pattern_username = r"^Username:"
    pattern_password = r"^Password:"
    command_exit = "logout"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_save_config = "save"
    pattern_prompt = r"(?P<hostname>\S+)(?:\(.*)?#"
    pattern_unpriveleged_prompt = \
        r"^(?P<hostname>[a-zA-Z0-9-_\.\/()]+)(?:-[a-zA-Z0-9/]+)*>$"
    pattern_syntax_error = \
        r"(% Unknown command, the error locates at \'^\'|  Logged Fail!|"
        r"System is busy, please try after a while)"
    rogue_chars = [
        re.compile(r"\n\r\s+Line \d+ operating, attempt of the Line -\d+ denied!\n\r"),
        "\r"
    ]

    def setup_session(self, script):
        script.cli("config", ignore_errors=True)
        script.cli("terminal type vt100", ignore_errors=True)
        script.cli("history size 0", ignore_errors=True)
        script.cli("length 0", cached=True, ignore_errors=True)
        script.cli("cls", ignore_errors=True)
