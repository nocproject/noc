# ---------------------------------------------------------------------
# Vendor: Opticin
# OS:     OS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Opticin.OS"

    pattern_unprivileged_prompt = rb"^(?P<hostname>[^\n]+)h>"
    pattern_syntax_error = (
        rb"% Unknown command|% Invalid input detected at|"
        rb"% Incomplete command|% Ambiguous command"
    )
    command_super = "enable"
    pattern_prompt = rb"^(?P<hostname>[^\n]+)\\enable>"
    pattern_more = [
        (rb"----------MORE------------", b" "),
        (rb"--- \[Space\] Next page, \[Enter\] Next line, \[A\] All, Others to exit ---", b" "),
        (rb"Startup configuration file name", b"\n"),
    ]
    config_volatile = ["\x08+"]
    rogue_chars = [b"\r"]
    command_submit = b"\r"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "copy config flash"
    convert_mac = BaseProfile.convert_mac_to_dashed

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("Port15")
        'Port 15'
        """
        s = s.replace("Port1", "Port 1")
        return s.replace("Port2", "Port 2")


#    def setup_session(self, script):
#        try:
#            script.cli("terminal length 0")
#        except script.CLISyntaxError:
#            pass
