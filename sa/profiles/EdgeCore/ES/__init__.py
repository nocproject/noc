# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: EdgeCore
## OS:     ES
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "EdgeCore.ES"
    pattern_unpriveleged_prompt = r"^(?P<hostname>[^\n]+)>"
    pattern_syntax_error = r"% Invalid input detected at|% Incomplete command"
    command_super = "enable"
    pattern_prompt = r"^(?P<hostname>[^\n]+)(?:\(config[^)]*\))?#"
    pattern_more = [
        (r"---?More---?", " "),
        (r"--- \[Space\] Next page, \[Enter\] Next line, \[A\] All, Others to exit ---", " "),
        (r"Startup configuration file name", "\n")
    ]
    config_volatile = ["\x08+"]
    rogue_chars = ["\r"]
    command_submit = "\r"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    convert_mac = BaseProfile.convert_mac_to_dashed

    rx_if_snmp_eth = re.compile(
        r"^Ethernet Port on Unit (?P<unit>\d+), port (?P<port>\d+)$",
        re.IGNORECASE
    )

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("Eth 1/ 1")
        'Eth 1/1'
        >>> Profile().convert_interface_name("Ethernet Port on unit 1, port 21")
        'Eth 1/21'
        """
        s = s.strip()
        match = self.rx_if_snmp_eth.match(s)
        if match:
            return "Eth %s/%s" % (match.group("unit"),
                                  match.group("port"))
        s = s.replace("  ", " ")
        return s.replace("/ ", "/")

    def setup_session(self, script):
        try:
            script.cli("terminal length 0")
        except script.CLISyntaxError:
            pass
