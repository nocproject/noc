# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: Ericsson
# OS:     BSC
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Ericsson.BSC"
    command_submit = "\r"
    command_enter_config = "configure"
    command_leave_config = "end"
    pattern_prompt = r"^(\S*[><]|\S+:\$)"
    rx_header = re.compile("(\S+)")

    class mml(object):
        """Switch context manager to use with "with" statement"""

        def __init__(self, script):
            self.script = script

        def __enter__(self):
            """Enter switch context"""
            self.script.cli("mml")

        def __exit__(self, exc_type, exc_val, exc_tb):
            """Leave switch context"""
            if exc_type is None:
                self.script.cli("EXIT;")

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
