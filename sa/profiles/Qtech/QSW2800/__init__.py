# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Qtech
## OS:     QSW2800
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles import Profile as NOCProfile


class Profile(NOCProfile):
    name = "Qtech.QSW2800"
    supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_username = r"^login:"
    pattern_password = r"^Password:"
    pattern_more = [
        (r"^\.\.\.\.press ENTER to next line, CTRL_C to break, other key to next page\.\.\.\.", "\n"),
        (r"^Startup config in flash will be updated, are you sure\(y/n\)\? \[n\]", "y\n"),
        (r"^ --More-- $", " "),
        (r"^Confirm to overwrite current startup-config configuration","\ny\n"),
        (r"^Confirm to overwrite the existed destination file?", "\ny\n"),
        (r"^Begin to receive file, please wait", " "),
        (r"#####"," ")
    ]
    pattern_unpriveleged_prompt = r"^\S+>"
    pattern_syntax_error = r" % Unrecognized command, and error detected at '\^' marker."
    command_disable_pager = "terminal length 0"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    command_submit = "\r"
    pattern_prompt = r"^\S+#"

    rx_ifname = re.compile(r"^(?:1/)?(?P<number>\d+)$")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("Ethernet1/1")
        'Ethernet1/1'
        >>> Profile().convert_interface_name("1")
        'Ethernet1/1'
        """
        match = self.rx_ifname.match(s)
        if match:
            return "Ethernet1/%d" % int(match.group("number"))
        else:
            return s
