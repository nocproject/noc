# ----------------------------------------------------------------------
# Vendor: Alcatel
# OS:     AOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.AOS"
    pattern_username = rb"[Ll]ogin :"
    pattern_password = rb"[Pp]assword :"
    pattern_prompt = rb"^(\S*->|(?P<hostname>\S+)# )"
    pattern_syntax_error = rb"ERROR: Invalid entry:"
    command_save_config = "write memory\r\ncopy working certified"
    command_exit = "exit"

    matchers = {
        "is_version_gte_6_3_4": {"version": {"$gte": r"6.3.4"}},
        "is_stack": {"caps": {"$in": ["Stack | Members"]}},
    }

    def convert_interface_name(self, s):
        if s.startswith("Alcatel ") or s.startswith("Alcatel-Lucent "):
            # Alcatel 1/2 6.3.1.871.R01
            # Alcatel-Lucent 1/13
            return s.split()[1]
        if s.startswith("Dynamic Aggregate Number "):
            # Dynamic Aggregate Number 1 ref 40000001 size 4
            return "Agg %s" % s.split()[3]
        return s
