# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: Alcatel
# OS:     AOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
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

    @classmethod
    def cmp_version(cls, x, y):
        a = [int(z) for z in cls.rx_ver.findall(x)]
        b = [int(z) for z in cls.rx_ver.findall(y)]
        return (a > b) - (a < b)

    def convert_interface_name(self, s):
        if s.startswith("Alcatel ") or s.startswith("Alcatel-Lucent "):
            # Alcatel 1/2 6.3.1.871.R01
            # Alcatel-Lucent 1/13
            return s.split()[1]
        elif s.startswith("Dynamic Aggregate Number "):
            # Dynamic Aggregate Number 1 ref 40000001 size 4
            return "Agg %s" % s.split()[3]
        return s
