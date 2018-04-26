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
    pattern_prompt = r"^(?P<hostname>[ \S]+)(\s\(\S+\)){0,3} #"
    pattern_more = [(r"^--More-- or \(q\)uit$", " "),
                    (r"This operation may take a few minutes.\n"
                     r"Management interfaces will not be available during this time.\n"
                     r"Are you sure you want to save\?\s*\(y/n\):\s*", "y\n"),
                    (r"Would you like to save them now\?", "n")]
    pattern_syntax_error = r"ERROR: Wrong or incomplete command"
    command_super = "enable"
    command_exit = "logout"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "write memory"

    @staticmethod
    def parse_kv_out(out):
        r = {}
        for line in out.splitlines():
            if "....." in line:
                el1, el2 = line.split(".....", 1)
                r[el1.strip(".").strip()] = el2.strip(".").strip()
        return r
