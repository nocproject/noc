# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Alstec
# OS:     24xx
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alstec.24xx"
    pattern_username = r"^User:"
    pattern_unprivileged_prompt = r"^(?P<hostname>[ \S]+) >"
    pattern_prompt = r"^(?P<hostname>[ \S]+) #"
    pattern_more = r"^--More-- or \(q\)uit$"
    pattern_syntax_error = r"ERROR: Wrong or incomplete command"
    command_super = "enable"
    command_exit = "logout"

    @staticmethod
    def parse_kv_out(out):
        r = {}
        for line in out.splitlines():
            if "....." in line:
                el1, el2 = line.split(".....", 1)
                r[el1.strip(".").strip()] = el2.strip(".").strip()
        return r
