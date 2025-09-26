# ---------------------------------------------------------------------
# Vendor: OS
# OS:     Linux
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python module
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "OS.Linux"

    # supported_schemes = [NOCProfile.TELNET, NOCProfile.SSH]
    pattern_username = rb"^((?!Last)\S+ login|[Ll]ogin):"
    pattern_password = rb"^[Pp]assword:"

    # use default BASH promt PS1='[\u@\h \W]\$ '
    # pattern_prompt = r"^\[\S+@\S+\s\S+](#|\$)\s"
    # Dropbear prompt - '84dfcdf:~$ ', \S+:~[>$]\s+
    # SSHD prompt - [admin@\S+:/root], \[admin@\S+:/root\]
    pattern_prompt = rb"(\[\S+@\S+\s\S+](#|\$)\s|\S+@\S+:\S+>|\S+:~[>$]\s+|\[admin@\S+:/root\])"
    pattern_syntax_error = (
        rb"^(bash: \S+: command not found...\r\n|-\w+: \w+: not found|"
        rb"-\w+: \w+: No such file or directory|\w+: \w+: command not found|"
        rb"\w+: \w+: \w+: No such file or directory)"
    )
    pattern_more = [
        (rb"--More--", b"\n"),
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
        return cls.INTERFACE_TYPES.get(name[:2].lower())

    rx_data = re.compile(
        r"^(?P<metric>[a-zA-Z0-9_]+)\{(?P<data>.*)\}\s+(?P<value>\S+)$", re.MULTILINE
    )
