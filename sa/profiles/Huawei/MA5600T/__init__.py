# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Huawei
# OS:     MA5600T
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile
import re


class Profile(BaseProfile):
    name = "Huawei.MA5600T"
    pattern_username = r"^>[>\s]User name(|\s\([<\s\w]+\)):"
    pattern_password = r"^>[>\s](?:User )?[Pp]assword(|\s\([<\s\w]+\)):"
    pattern_more = [
        (r"---- More \( Press 'Q' to break \) ----", " "),
        (r"\[<frameId/slotId>\]", "\n"),
        (r"\(y/n\) \[n\]", "y\n"),
        (r"\[to\]\:", "\n"),
        (r"\{ \<cr\>\|vpi\<K\> \}\:", "\n"),
        (r"\{ \<cr\>\|ont\<K\> \}\:", "\n"),
        (r"Are you sure to modify system time?", "n\n"),
        (r"Are you sure to log out?", "y\n"),
        (r"\{ <cr>\|configuration<K>\|data<K> \}", "\n"),
        (r"\{ <cr>\|mode<K> \}", "\n")
    ]
    pattern_unprivileged_prompt = r"^(?P<hostname>(?!>)\S+?)>"
    pattern_prompt = \
        r"^(?P<hostname>(?!>)\S+?)(?:-\d+)?(?:\(config\S*[^\)]*\))?#"
    pattern_syntax_error = r"(% Unknown command|  Incorrect command:)"
    command_more = " "
    config_volatile = ["^%.*?$"]
    command_disable_pager = "scroll 512"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "quit"
    command_save_config = "save\ny\n"
    command_exit = "quit\ny\n"
    rogue_chars = ["\xff", "\r"]

    rx_slots = re.compile("^\s*\d+", re.MULTILINE)
    rx_ports = re.compile(
        "^\s*\d+\s+(?P<type>ADSL|VDSL|GPON|10GE|GE|FE)\s+.+?"
        "(?P<state>[Oo]nline|[Oo]ffline|Activating|Activated)",
        re.MULTILINE)

    def get_slots_n(self, script):
        """
        If slots 7 - MA5603, 14 - MA5600
        :param script:
        :return:
        """
        i = -1
        v = script.cli("display board 0", cached=True)
        for match in self.rx_slots.finditer(v):
            i += 1
        return i + 1

    def get_ports_n(self, script, slot_no):
        i = -1
        t = ""
        s = []
        v = script.cli(("display board 0/%d" % slot_no), cached=True)
        for match in self.rx_ports.finditer(v):
            i += 1
            t = match.group("type")
            s += [match.group("state") in ["Online", "online", "Activated"]]
        return {"n": i, "t": t, "s": s}

    def fill_ports(self, script):
        n = self.get_slots_n(script)
        r = []
        i = 0
        while i <= n:
            r += [self.get_ports_n(script, i)]
            i += 1
        return r

    def convert_interface_name(self, interface):
        if " " in interface:
            return interface.split()[1]
        if "ethernet" in interface:
            return interface[8:]
        return interface
