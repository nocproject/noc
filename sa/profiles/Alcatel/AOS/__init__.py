# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Vendor: Alcatel
# OS:     AOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.AOS"
    pattern_username = "[Ll]ogin :"
    pattern_password = "[Pp]assword :"
    pattern_prompt = r"^(\S*->|(?P<hostname>\S+)# )"
    pattern_syntax_error = "ERROR: Invalid entry:"
    command_save_config = "write memory\r\ncopy working certified"
    command_exit = "exit"

    rx_ver = re.compile(r"\d+")

    def cmp_version(self, x, y):
        return cmp(
            [int(z) for z in self.rx_ver.findall(x)],
            [int(z) for z in self.rx_ver.findall(y)]
        )

    def convert_interface_name(self, s):
        if s.startswith("Alcatel ") or s.startswith("Alcatel-Lucent "):
            # Alcatel 1/2 6.3.1.871.R01
            # Alcatel-Lucent 1/13
            return s.split()[1]
        elif s.startswith("Dynamic Aggregate Number "):
            # Dynamic Aggregate Number 1 ref 40000001 size 4
            return "Agg %s" % s.split()[3]
        else:
            return s
=======
##----------------------------------------------------------------------
## Vendor: Alcatel
## OS:     AOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Alcatel.AOS"
    supported_schemes = [TELNET, SSH]
    pattern_username = "[Ll]ogin :"
    pattern_password = "[Pp]assword :"
    pattern_prompt = r"^(\S*->|(?P<hostname>\S+)# )"
    command_save_config = "write memory\r\ncopy working certified"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
