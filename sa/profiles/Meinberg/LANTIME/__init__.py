# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: MEINBERG
# OS:     LANTIME
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Meinberg.LANTIME"

    # supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_username = "^((?!Last)\S+ login|[Ll]ogin):"
    pattern_password = "^[Pp]assword:"

    # use default BASH promt PS1='[\u@\h \W]\$ '
    # pattern_prompt = r"^\[\S+@\S+\s\S+](#|\$)\s"
    pattern_prompt = r"\[\S+@\S+\s\S+](#|\$)\s"
    pattern_syntax_error = (
        r"^(bash: \S+: command not found...\r\n|-\w+: \w+: not found|"
        r"-\w+: \w+: No such file or directory|\w+: \w+: command not found|"
        r"\w+: \w+: \w+: No such file or directory)"
    )
    # pattern_more = [
    #    (r"Install package.*\[N/y\]\s$", "\n"),
    #    (r"Is this ok \[y/N\]: ", "y\n")
    # ]
    command_disable_pager = "LANG=en_US.UTF-8 ; PATH=$PATH:/sbin:/usr/sbin ; PROMPT_COMMAND=''"
    command_super = "sudo bash"
    command_exit = "exit"
    command_more = "\n"
