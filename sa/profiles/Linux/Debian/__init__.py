# -*- coding: utf-8 -*-
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
    pattern_username = "^((?!Last)\S+ login|[Ll]ogin):"
    pattern_password = "^[Pp]assword:"

    '''
    "user@debian-test-virtual:~$ "
    "root@debian-test-virtual:/home/user# "
    '''
<<<<<<< HEAD
=======
    # 
    # use default BASH promt PS1='[\u@\h \W]\$ '
    # pattern_prompt = r"^\[\S+@\S+\s\S+](#|\$)\s"
>>>>>>> 82dd005bcaecaccb471dc39bfbd15fc4a9d69697
    pattern_prompt = r"\S+@\S+(#|:\~$|\$)\s"
    pattern_syntax_error = \
        r"^(bash: \S+: command not found...\r\n|-\w+: \w+: not found|" \
        r"-\w+: \w+: No such file or directory|\w+: \w+: command not found|" \
        r"\w+: \w+: \w+: No such file or directory)"
    pattern_more = [
        (r"Install package.*\[N/y\]\s$", "\n"),
        (r"Is this ok \[y/N\]: ", "y\n")
    ]
    command_disable_pager = \
        "LANG=en_US.UTF-8 ; PATH=$PATH:/sbin:/usr/sbin ; PROMPT_COMMAND=''"
    command_super = "sudo bash"
    command_exit = "exit"
    command_more = "\n"

<<<<<<< HEAD
    # def setup_session(self, script):
    #     script.cli("config", ignore_errors=True)
=======
    #def setup_session(self, script):
    #     script.cli("config", ignore_errors=True)
>>>>>>> 82dd005bcaecaccb471dc39bfbd15fc4a9d69697
