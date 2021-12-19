# ---------------------------------------------------------------------
# Vendor: Zhone
# OS:     Bitstorm
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Zhone.Bitstorm"

    # pattern_unprivileged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_username = rb"Login>"
    username_submit = b"\r"
    password_submit = b"\r"
    command_submit = b"\r"
    command_disable_pager = "paging disable"
    pattern_password = rb"Password>"
    # pattern_prompt = r"^(?P<hostname>\S+)\s*[#>]"
    # pattern_prompt = r"^(?P<hostname>\S+)(?<!Login)(?<!Password)\s*[#>]"
    pattern_prompt = (
        rb"^[\s\*]*(?P<hostname>[\S\s]+)(?<!Login)(?<!Password)\s*(\(\S+\)){0,4}(]|)[#>]"
    )
    pattern_syntax_error = r"Syntax error"
    pattern_operation_error = r"ERROR: Permission denied."
    pattern_more = [(rb"<SPACE> for next page, <CR> for next line, A for all, Q to quit", b"a")]
    command_exit = "exit"

    def convert_interface_name(self, s):
        s = s.lower().strip()
        if " " in s:
            # SNMP Output ifName
            name, num = s.rsplit(" ", 1)
            if name.startswith("ethernet"):
                s = "eth" + num
            elif name.startswith("dsl port"):
                # DSL PORT 5
                s = num
            elif name == "dsl":
                # dsl 6
                s = num
            elif name.startswith("dsl ethernet interface"):
                # DSL Ethernet Interface
                s = "dsl_ethernet" + num
            elif name.startswith("dsl atm interface"):
                # DSL ATM Interface
                s = "dsl_atm" + num
            elif name.startswith("management in-band ethernet interface"):
                s = "mgmt_i"
            elif name.startswith("'management out-of-band ethernet interface"):
                s = "mgmt_o"
            elif num.isdigit():
                s = name.replace(" ", "_") + num
        return s
