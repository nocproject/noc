# ---------------------------------------------------------------------
# Vendor: Linux
# OS:     ALT
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python module
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Linux.Alt"

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
    pattern_more = [
        (rb"Install package.*\[N/y\]\s$", b"\n"),
        (rb"Is this ok \[y/N\]: ", b"y\n"),
    ]
    command_disable_pager = "LANG=en_US.UTF-8; PATH=$PATH:/sbin:/usr/sbin; PROMPT_COMMAND=''"
    command_super = b"sudo bash"
    command_exit = "exit"

    INTERFACE_TYPES = {
        "et": "physical",  # No comment
        "bo": "physical",
        "en": "physical",
        "lo": "loopback",  # No comment
    }

    @classmethod
    def get_interface_type(cls, name):
        c = cls.INTERFACE_TYPES.get(name[:2].lower())
        return c

    rx_data = re.compile(
        r"^(?P<metric>[a-zA-Z0-9_]+)\{(?P<data>.*)\}\s+(?P<value>\S+)$", re.MULTILINE
    )
