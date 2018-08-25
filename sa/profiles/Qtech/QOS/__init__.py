# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     QOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

#SNMPv2-MIB::sysObjectID.0 = OID: SNMPv2-SMI::enterprises.27514.6.178

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Qtech.QOS"
    pattern_more = [
        (r"^ --More-- $", " "),
        (r"^Confirm to overwrite current startup-config configuration "
            r"[Y/N]:", "\nY\n"),
        (r"^Confirm to overwrite current startup-config configuration",
            "\ny\n"),
        (r"^Confirm to overwrite the existed destination file?", "\ny\n"),
    ]
    pattern_unprivileged_prompt = r"^\S+>"
    pattern_syntax_error = r"% (?:Invalid input detected at '\^' marker|" \
                           r"(?:Ambiguous|Incomplete|.+Unknown) command)|" \
                           r"Error input in the position market by"
    command_disable_pager = "terminal page-break disable"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    command_submit = "\r"
    pattern_prompt = \
        r"^(?P<hostname>[a-zA-Z0-9]\S{0,19})(?:[\.\-_\d\w]+)?" \
        r"(?:\(config[^\)]*\))?#"

    rx_ifname = re.compile(r"^(?P<number>\d+)$")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("1")
        'P1'
        """
        match = self.rx_ifname.match(s)
        if match:
            return "P%d" % int(match.group("number"))
        else:
            return s
