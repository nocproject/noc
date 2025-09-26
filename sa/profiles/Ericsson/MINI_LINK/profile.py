# ---------------------------------------------------------------------
# Vendor: Ericsson
# OS:     MINI_LINK
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Ericsson.MINI_LINK"

    pattern_more = [(rb"^---(more)---", b"\n")]
    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)>"
    pattern_prompt = rb"^(?P<hostname>\S+)#"
    pattern_syntax_error = rb"% Invalid input at"
    command_super = b"enable"
    command_enter_config = "configure"
    command_leave_config = "exit"

    INTERFACE_TYPES = {
        "Ethernet": "physical",
        "Loopback": "loopback",
        "Tunnel": "tunnel",
        "PPP": "tunnel",
    }

    def setup_script(self, script):
        script.cli("")  # Do not remove thid. Need to build prompt pattern
        self.add_script_method(script, "cli_clean", self.cli_clean)

    def cli_clean(self, script, cmd, cached=False):
        """
        Modify rogue_chars pattern
        :param script:
        :param cmd:
        :param cached:
        :return:
        """
        prompt = script.get_cli_stream().patterns["prompt"].pattern
        prompt = prompt.replace("^", "")
        prompt = prompt.replace("\\", "")
        r = cmd[0] + "(\x08)+" + prompt
        self.rogue_chars = [re.compile(rb"%s" % r), b"\r"]
        if cached:
            return script.cli(cmd, cached=True)
        return script.cli(cmd)
