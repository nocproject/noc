# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     QSW
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Qtech.QSW"
    pattern_username = r"^(Username\(1-32 chars\)|[Ll]ogin):"
    pattern_password = r"^Password(\(1-16 chars\)|):"
    pattern_more = [
        (r"^\.\.\.\.press ENTER to next line, CTRL_C to break, other key "
            r"to next page\.\.\.\.", " "),
        (r"^Startup config in flash will be updated, are you sure\(y/n\)\? "
            r"\[n\]", "y"),
        (r"^ --More-- $", " "),
        (r"^Confirm to overwrite current startup-config configuration",
            "\ny\n"),
        (r"^Confirm to overwrite the existed destination file?", "\ny\n"),
        (r"^Begin to receive file, please wait", " "),
        (r"#####", " ")
    ]
    pattern_unprivileged_prompt = r"^\S+>"
    pattern_syntax_error = \
        r"% (Unrecognized command, and error|Invalid input) detected at " \
        r"'\^' marker.|% Ambiguous command:|interface error!|Incomplete " \
        r"command"
#    command_disable_pager = "terminal datadump"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_exit = "quit"
    command_save_config = "copy running-config startup-config"
    pattern_prompt = r"^\S+#"
    rogue_chars = [re.compile(r"\s*\x1b\[74D\s+\x1b\[74D"), "\r"]
    rx_ifname = re.compile(r"^(?P<number>[\d/]+)$")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("1/1")
        'e1/1'
        >>> Profile().convert_interface_name("e1/1")
        'e1/1'
        """
        match = self.rx_ifname.search(s)
        if match:
            return "e%s" % s
        else:
            return s

    def get_interface_names(self, name):
        r = []
        if name.startswith("port "):
            r += [name[5:]]
        else:
            r += [name]
        return r
