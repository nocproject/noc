# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     DSLAM
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.DSLAM"
    pattern_username = r"(?<!Last )[Ll]ogin: "
    pattern_more = [
        (r"--More-- ", " "),
        (r"\[Yes/press any key for no\]", "Y")
    ]
    pattern_prompt = r"(?P<hostname>\S+)> "
    pattern_syntax_error = r"Command not found"
#    command_disable_pager = "terminal datadump"
#    command_super = "enable"
    username_submit = "\r"
    password_submit = "\r"
    command_submit = "\r"

    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "save"
    rx_header = re.compile("(\S+)")

    def iter_items(self, s):
        def iter_lines(s):
            lines = s.splitlines()
            # Skip until empty line
            if "" in lines:
                i = lines.index("") + 1
            else:
                i = 0
            ll = len(lines) - 2
            while i <= ll:
                yield lines[i], lines[i + 1]
                i += 3

        def parse_line(key, value):
            pos = [match.start() for match in self.rx_header.finditer(key)]
            ranges = [(s, e) for s, e in zip(pos, pos[1:])]
            if not ranges:
                return {}
            ranges += [(ranges[-1][1], None)]
            d = {}
            for s, e in ranges:
                d[key[s:e].strip()] = value[s:e].strip()
            return d

        d = {}
        for kl, vl in iter_lines(s):
            if not vl or not kl:
                continue
            if kl[0] == " ":
                d.update(parse_line(kl, vl))
            else:
                if d:
                    yield d
                d = parse_line(kl, vl)
        if d:
            yield d