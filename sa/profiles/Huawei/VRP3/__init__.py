# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Huawei
# OS:     VRP3
# Compatible: 3.1
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Huawei.VRP3"
    pattern_username = r"^>(?:\>| )User name( \(<\d+ chars\))?:"
    pattern_password = r"^>(?:\>| )(?:User )?[Pp]assword( \(<\d+ chars\))?:"
    pattern_more = [
        (r"^--More\(Enter: next line, spacebar: next page, "
         r"any other key: quit\)--", " "), (r"\[<frameId/slotId>\]", "\n"),
        (r"\(y/n\) \[n\]", "y\n"), (r"\[to\]\:", "\n")
    ]
    # Do not match this line: "\r\n>>User name: "
    pattern_unprivileged_prompt = r"^[^>]\S+?>"
    pattern_prompt = r"^(?P<hostname>\S+?)(?:-\d+)?(?:\(config\S*[^\)]*\))?#"
    pattern_syntax_error = r"Invalid parameter|Incorrect command"
    command_more = " "
    config_volatile = ["^%.*?$"]
    command_disable_pager = "length 0"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "save\ny\n"

    rx_interface_name = re.compile(r"^(?P<type>\S+)\s+(?P<number>\S.*)", re.MULTILINE)

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("ADL 0/1/1")
        'ADSL:0/1/1'
        >>> Profile().convert_interface_name("ADL   0   1   1")
        'ADSL:0/1/1'
        """

        if ":" in s or "mgmt" is s:
            return s
        match = self.rx_interface_name.match(s)
        if not match:
            return s
        if "/" not in match.group("number"):
            number = "/".join(match.group("number").split())
        else:
            number = match.group("number")
        return "%s:%s" % ({"ADL": "ADSL", "HDL": "HDSL"}[match.group("type")], number)
