# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     TAU
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.TAU"

    pattern_username = rb"^\S+ [Ll]ogin:"
    pattern_password = rb"^[Pp]assword:"
    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)>\s*"
    pattern_prompt = rb"^(\S+# |> |config> |\[\S+\]\s*|root@\S+:(~|/\S+)\$)"
    pattern_more = [
        (rb'Press any key to continue|\| Press any key to continue \| Press "q" to exit \| ', b"\n")
    ]
    pattern_syntax_error = rb"Syntax error: Unknown command|-sh: .+: not found"
    command_exit = "exit"
    command_enter_config = "config"
    command_leave_config = "exit"
    command_super = b"enable"
    rogue_chars = [re.compile(rb"\^J"), b"\r"]

    matchers = {
        "is_tau4": {"platform": {"$regex": r"^TAU\-4"}},
        "is_tau8": {"platform": {"$regex": r"^TAU-8"}},
        "is_tau36": {"platform": {"$regex": r"^TAU-36"}},
    }

    already_in_shell = False

    def setup_session(self, script):
        try:
            script.cli("show hwaddr", cached=True)
            script.cli("shell", ignore_errors=True)
            self.already_in_shell = False
        except script.CLISyntaxError:
            self.already_in_shell = True

    def shutdown_session(self, script):
        if not self.already_in_shell:
            script.cli("exit\r", ignore_errors=True)

    empty_lines = re.compile(r"(?:\n){3,}", re.MULTILINE)
    empty_spaces = re.compile(r"^\s+\n", re.MULTILINE)

    def cleaned_config(self, config):
        config = config.replace("cat: read error: Is a directory\n", "")
        config = self.empty_lines.sub("\n\n", config)
        config = self.empty_spaces.sub("\n", config)
        return super().cleaned_config(config)

    INTERFACE_TYPES = {
        "e": "physical",  # Ethernet
        "p": "physical",  # Virtual Ethernet
        "b": "physical",  # Bridge
        "l": "loopback",  # Local Loopback
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:1])
