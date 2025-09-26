# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     QOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# SNMPv2-MIB::sysObjectID.0 = OID: SNMPv2-SMI::enterprises.27514.6.178

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Qtech.QOS"

    pattern_more = [
        (rb"^ --More-- $", b" "),
        (rb"^Confirm to overwrite current startup-config configuration [Y/N]:", b"\nY\n"),
        (rb"^Confirm to overwrite current startup-config configuration", b"\ny\n"),
        (rb"^Confirm to overwrite the existed destination file?", b"\ny\n"),
    ]
    pattern_unprivileged_prompt = rb"^\S+>"
    pattern_syntax_error = (
        rb"% (?:Invalid input detected at '\^' marker|"
        rb"(?:Ambiguous|Incomplete|.+Unknown) command)|"
        rb"Error input in the position market by"
    )
    command_disable_pager = "terminal page-break disable"
    command_super = b"enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    command_submit = b"\r"
    pattern_prompt = rb"^(?P<hostname>[a-zA-Z0-9]\S{0,19})(?:[\.\-_\d\w]+)?(?:\(config[^\)]*\))?#"

    rx_ifname = re.compile(r"^P(?P<number>\d+)$")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("P1")
        'port1'
        """
        match = self.rx_ifname.match(s)
        if match:
            return "port%d" % int(match.group("number"))
        return s
