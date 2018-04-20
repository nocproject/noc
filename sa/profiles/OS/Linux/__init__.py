# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: GNU
# OS:     GNU/Linux
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "OS.Linux"
    pattern_username = "^((?!Last)\S+ login|[Ll]ogin):"
    pattern_unprivileged_prompt = r"^\[?\s*\w+@(?P<hostname>\S+)\]?(\s+|:)\S+\s*\]?\$\s*"
=======
##----------------------------------------------------------------------
## Vendor: GNU
## OS:     GNU/Linux
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
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
    pattern_unpriveleged_prompt = r"^\[?\s*\w+@(?P<hostname>\S+)\]?(\s+|:)\S+\s*\]?\$\s*"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_prompt = r"^(\[?\s*root@(?P<hostname>\S+)\]?(\s+|:)\S+\s*(#|\$)\s*|\S+:~>\s+|\[admin@\S+:/root\])"
    pattern_syntax_error = r"^(-\w+: \w+: not found|-\w+: \w+: No such file or directory|\w+: \w+: command not found|\w+: \w+: \w+: No such file or directory)"
    command_disable_pager = "export LANG=en_GB.UTF-8"
    command_super = "su"
    command_exit = "exit"
    pattern_more = "--More--"
    command_more = "\n"
