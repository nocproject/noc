# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Qtech
## OS:     QSW
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

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
        (r"^ --More-- $", " ")
        ]
    pattern_unpriveleged_prompt = r"^\S+>"
    pattern_syntax_error = r"% (Unrecognized command, and error|Invalid input) detected at '\^' marker.|% Ambiguous command:"
#    command_disable_pager = "terminal datadump"
    command_super = "enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    pattern_prompt = r"^\S+#"
#    convert_interface_name = NOCProfile.convert_interface_name_cisco
