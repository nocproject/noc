# ---------------------------------------------------------------------
# Vendor: Maipu
# OS:     OS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Maipu.OS"

    pattern_more = [
        (rb"^---MORE---\r", b" "),
        (rb"^---MORE---", b" "),
        (rb"^....press ENTER to next line, Q to quit, other key to next page....", b"\n"),
        # (rb"Are you sure to overwrite /flash/startup (Yes|No)?", b"Yes"),
        (rb"Startup config in flash will be updated, are you sure", b"y"),
    ]

    command_exit = "quit"
    command_super = b"enable"
    command_enter_config = "configure t"
    command_leave_config = "end"
    command_save_config = "save"

    pattern_syntax_error = rb"% Unrecognized command, and error detected at \'^\' marker."
    pattern_unprivileged_prompt = rb"^(?P<hostname>[a-zA-Z0-9-_\.]+)(?:-[a-zA-Z0-9/]+)*>$"
    pattern_prompt = rb"^(?P<hostname>[a-zA-Z0-9-_\.]+)(?:-[a-zA-Z0-9/]+)(\(config\))*[*\)>#]$"

    rogue_chars = [b"             \r", b"\r"]

    INTERFACE_TYPES = {
        "te": "physical",  # tengigabitethernet
        "gi": "physical",  # gigabitethernet
        "25ge": "physical",  # 25gigabitethernet
        "100ge": "physical",  # 100gigabitethernet
        "dc": "other",
        "vlan": "SVI",
        "null": "null",
        "loopback": "loopback",
    }

    rx_module_info = re.compile(
        r"^(?P<module_name>\S+\s\d+)\s+(?P<online>\S+)\s+(?P<state>(Start Ok|Normal))\s+(?P<part_no>[^ ,]+)\s+(?P<serial>\S+)\s+$",
        re.MULTILINE | re.IGNORECASE,
    )

    @classmethod
    def get_interface_type(cls, name):
        for x in cls.INTERFACE_TYPES:
            if not name.startswith(x):
                continue
            return cls.INTERFACE_TYPES[x]
