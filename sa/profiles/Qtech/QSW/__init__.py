# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Qtech
## OS:     QSW
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
## NOC modules
from noc.sa.profiles import Profile as NOCProfile
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(NOCProfile):
    name = "Qtech.QSW"
    supported_schemes = [TELNET, SSH]
    pattern_username = r"^(Username\(1-32 chars\)|[Ll]ogin):"
    pattern_password = r"^Password(\(1-16 chars\)|):"
    pattern_more = [
        (r"^\.\.\.\.press ENTER to next line, CTRL_C to break, other key to next page\.\.\.\.", "\n"),
        (r"^Startup config in flash will be updated, are you sure\(y/n\)\? \[n\]", "y"),
        (r"^ --More-- $", " "),
        (r"^Confirm to overwrite current startup-config configuration","\ny\n"),
        (r"^Confirm to overwrite the existed destination file?", "\ny\n"),
        (r"^Begin to receive file, please wait", " "),
        (r"#####"," ")
        ]
    pattern_unpriveleged_prompt = r"^\S+>"
    pattern_syntax_error = r"% (Unrecognized command, and error|Invalid input) detected at '\^' marker.|% Ambiguous command:|interface error!"
#    command_disable_pager = "terminal datadump"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
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
