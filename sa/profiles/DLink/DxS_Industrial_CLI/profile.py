# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: DLink
# OS:     DxS_Industrial_CLI
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DLink.DxS_Industrial_CLI"
    pattern_more = r"CTRL\+C.+?a A[Ll][Ll]\s*"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+?)>"
    pattern_prompt = r"^(?P<hostname>\S+?)#"
    pattern_syntax_error = r"% Invalid input detected at"
    command_disable_pager = "terminal length 0"
    command_more = "a"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "copy running-config startup-config\n"
    command_exit = "logout"

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("eth1/0/1")
        'Eth1/0/1'
        >>> Profile().convert_interface_name("1/1")
        'Eth1/0/1'
        """
        if s.startswith("eth"):
            return "E%s" % s[1:]
        elif s.startswith("1/"):
            return "Eth1/0/%s" % s[2:]
        else:
            return s
