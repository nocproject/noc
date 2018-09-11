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
        (r"\s*---- More \(Press CTRL\+C break\) ---\s*", " "),
        (r"Note: Terminal", "\n"),
        (r"Warning: Battery is low power!", "\n"),
        (r"\{\s<cr>.*\s\}:", "\n"),
        (r"^Are you sure?\[Y/N\]", "y\n"),
        (r"^\{ terminal\<K\> \}\:", "terminal\n")
    ]
    pattern_username = r"^Username:"
    pattern_password = r"^Password:"
    command_exit = "logout"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_save_config = "save"
    pattern_prompt = r"(?P<hostname>\S+)(?:\(.*)?#"
    pattern_unprivileged_prompt = \
        r"^(?P<hostname>[a-zA-Z0-9-_\.\/()]+)(?:-[a-zA-Z0-9/]+)*>$"
    pattern_syntax_error = \
        r"(% Unknown command, the error locates at \'^\'|  Logged Fail!|" \
        r"System is busy, please try after a while)"
    rogue_chars = [
        re.compile(r"\x1b\[39D\s+\x1b\[39D"),
        re.compile(r"\n\r\s+Line \d+ operating, attempt of the Line -\d+ denied!\n\r"),
        re.compile(r"\r\n\s+Note: Terminal users login \(IP: \S+ \)"),
        re.compile(r"\r\nWarning: Battery is low power!"),
        "\r"
    ]
    # to one SNMP GET request
    snmp_metrics_get_chunk = 8
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 5

    def setup_session(self, script):
        script.cli("terminal type vt100", ignore_errors=True)
        script.cli("no debug all", ignore_errors=True)
        script.cli("config", ignore_errors=True)
        script.cli("line vty 0 3", ignore_errors=True)
        script.cli("history size 0", ignore_errors=True)
        script.cli("length 0", ignore_errors=True)
        script.cli("exit", ignore_errors=True)
        script.cli("cls", ignore_errors=True)

    def shutdown_session(self, script):
        script.cli("config", ignore_errors=True)
        script.cli("line vty 0 3", ignore_errors=True)
        script.cli("no length 0", ignore_errors=True)
        script.cli("exit", ignore_errors=True)
