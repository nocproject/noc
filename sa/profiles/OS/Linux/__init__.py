# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: GNU
## OS:     GNU/Linux
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "OS.Linux"
    pattern_username = "^((?!Last)\S+ login|[Ll]ogin):"
    pattern_unpriveleged_prompt = r"^\[?\s*\w+@(?P<hostname>\S+)\]?(\s+|:)\S+\s*\]?\$\s*"
    pattern_prompt = r"^(\[?\s*root@(?P<hostname>\S+)\]?(\s+|:)\S+\s*(#|\$)\s*|\S+:~>\s+|\[admin@\S+:/root\])"
    pattern_syntax_error = r"^(-\w+: \w+: not found|-\w+: \w+: No such file or directory|\w+: \w+: command not found|\w+: \w+: \w+: No such file or directory)"
    command_disable_pager = "export LANG=en_GB.UTF-8"
    command_super = "su"
    command_exit = "exit"
    pattern_more = "--More--"
    command_more = "\n"
