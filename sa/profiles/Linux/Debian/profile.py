# ---------------------------------------------------------------------
# Vendor: Linux
# OS:     Debian
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Linux.Debian"

    # supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_username = rb"^((?!Last)\S+ login|[Ll]ogin):"
    pattern_password = rb"^[Pp]assword:"

    """
    "user@debian-test-virtual:~$ "
    "root@debian-test-virtual:/home/user# "
    """
    pattern_prompt = rb"\S+@\S+(#|:\~$|\$)\s"
    pattern_syntax_error = (
        rb"^(bash: \S+: command not found...\r\n|-\w+: \w+: not found|"
        rb"-\w+: \w+: No such file or directory|\w+: \w+: command not found|"
        rb"\w+: \w+: \w+: No such file or directory)"
    )
    pattern_more = [(rb"Install package.*\[N/y\]\s$", b"\n"), (rb"Is this ok \[y/N\]: ", b"y\n")]
    command_disable_pager = "LANG=en_US.UTF-8 ; PATH=$PATH:/sbin:/usr/sbin ; PROMPT_COMMAND=''"
    command_super = b"sudo bash"
    command_exit = "exit"

    # def setup_session(self, script):
    #     script.cli("config", ignore_errors=True)
