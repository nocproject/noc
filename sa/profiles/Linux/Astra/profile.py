# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Linux
# OS:     Astra
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python module
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Linux.Astra"

    # supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_username = r"^((?!Last)\S+ login|[Ll]ogin):"
    pattern_password = r"^[Pp]assword:"

    """
    "user@debian-test-virtual:~$ "
    "root@debian-test-virtual:/home/user# "
    """
    pattern_unprivileged_prompt = r"\S+@\S+(:\~$|\$)\s"
    pattern_prompt = r"\S+@\S+#\s"
    pattern_syntax_error = (
        r"^(bash: \S+: command not found...\r\n|-\w+: \w+: not found|"
        r"-\w+: \w+: No such file or directory|\w+: \w+: command not found|"
        r"\w+: \w+: \w+: No such file or directory)"
    )
    pattern_more = [
        (r"Install package.*\[N/y\]\s$", "\n"),
        (r"Is this ok \[y/N\]: ", "y\n"),
    ]
    command_disable_pager = "LANG=en_US.UTF-8; PATH=$PATH:/sbin:/usr/sbin; PROMPT_COMMAND=''"
    command_super = "sudo bash"
    command_exit = "exit"
    command_more = "\n"

    INTERFACE_TYPES = {
        "et": "physical",  # No comment
        "bo": "physical",
        "lo": "loopback",  # No comment
    }

    @classmethod
    def get_interface_type(cls, name):
        c = cls.INTERFACE_TYPES.get(name[:2].lower())
        return c

    rx_data = re.compile(
        r"^(?P<metric>[a-zA-Z0-9_]+)\{(?P<data>.*)\}\s+(?P<value>\S+)$", re.MULTILINE
    )
