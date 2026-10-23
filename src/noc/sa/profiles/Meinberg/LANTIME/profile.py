# ---------------------------------------------------------------------
# Vendor: MEINBERG
# OS:     LANTIME
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Meinberg.LANTIME"

    # supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_username = rb"^((?!Last)\S+ login|[Ll]ogin):"
    pattern_password = rb"^[Pp]assword:"

    # use default BASH promt PS1='[\u@\h \W]\$ '
    # pattern_prompt = r"^\[\S+@\S+\s\S+](#|\$)\s"
    pattern_prompt = rb"\[\S+@\S+\s\S+](#|\$)\s"
    pattern_syntax_error = (
        rb"^(bash: \S+: command not found...\r\n|-\w+: \w+: not found|"
        rb"-\w+: \w+: No such file or directory|\w+: \w+: command not found|"
        rb"\w+: \w+: \w+: No such file or directory)"
    )
    # pattern_more = [
    #    (r"Install package.*\[N/y\]\s$", "\n"),
    #    (r"Is this ok \[y/N\]: ", "y\n")
    # ]
    command_disable_pager = "LANG=en_US.UTF-8 ; PATH=$PATH:/sbin:/usr/sbin ; PROMPT_COMMAND=''"
    command_super = b"sudo bash"
    command_exit = "exit"
