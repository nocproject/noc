# ---------------------------------------------------------------------
# Vendor: Alstec
# OS:     7200
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alstec.7200"
    pattern_username = rb"^User:"
    pattern_unprivileged_prompt = rb"^\S+ >"
    pattern_prompt = rb"^\S+ #"
    pattern_more = [(rb"^--More-- or \(q\)uit$", b"\n")]
    pattern_syntax_error = rb"^(% Invalid input detected at|Command not found)"
    command_super = b"enable"
    command_exit = "exit\nexit"

    terminal_length_changed = False
    terminal_length = 0
    rx_length = re.compile(r"^Terminal length\.+ (?P<length>\d+)", re.MULTILINE)

    def setup_session(self, script):
        match = self.rx_length.search(script.cli("show terminal length"))
        if int(match.group("length")) != 0:
            self.terminal_length = match.group("length")
            self.terminal_length_changed = True
            script.logger.debug("Disabling CLI Paging...")
            script.cli("terminal length 0")

    def shutdown_session(self, script):
        if self.terminal_length_changed:
            script.cli("terminal length %s" % self.terminal_length)

    rx_cards = re.compile(r"^0/(?P<slot>\d+)\s*(?P<state>Working)?", re.MULTILINE)

    def fill_cards(self, script):
        r = []
        i = 0
        v = script.cli(("show xchassis cards"), cached=True)
        for match in self.rx_cards.finditer(v):
            i += 1
            s = bool(match.group("state"))
            r += [{"n": i, "s": s}]
        return r
