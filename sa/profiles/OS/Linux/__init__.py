# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: GNU
## OS:     GNU/Linux
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "OS.Linux"
    supported_schemes = [TELNET, SSH]
    pattern_username = "^((?!Last)\S+ login|[Ll]ogin):"
    pattern_password = "^[Pp]assword:"
    pattern_unpriveleged_prompt = r"^\w+.+\w+.~ ?\$"
    pattern_prompt = r"^(\S*?.?~? ?# ?|\S+:~> |\[admin+@\w+:/root+\]|\[root+@\w+ /root+\]\$)"
    pattern_syntax_error = r"^(-\w+: \w+: not found|-\w+: \w+: No such file or directory|\w+: \w+: command not found|\w+: \w+: \w+: No such file or directory)"
    command_disable_pager = "export LANG=en_GB.UTF-8"
    command_super = "su"
    command_exit = "exit"
    pattern_more = "--More--"
    command_more = "\n"
