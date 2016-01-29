# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Alcatel
## OS:     AOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.AOS"
    pattern_username = "[Ll]ogin :"
    pattern_password = "[Pp]assword :"
    pattern_prompt = r"^(\S*->|(?P<hostname>\S+)# )"
    command_save_config = "write memory\r\ncopy working certified"

    def convert_interface_name(self, s):
        if s.startswith("Alcatel "):
            # Alcatel 1/2 6.3.1.871.R01
            return s.split()[1]
        elif s.startswith("Dynamic Aggregate Number "):
            # Dynamic Aggregate Number 1 ref 40000001 size 4
            return "Agg %s" % s.split()[3]
        else:
            return s
