# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: HP
# OS:     Comware
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.Comware"
    command_more = " "
    command_exit = "quit"
    pattern_more = [(r"^\s+---- More ----$", " ")]
    pattern_prompt = r"^[<\[]\S+[>\]]"
    pattern_syntax_error = (
        r"% (?:Unrecognized command|Too many parameters|Incomplete command)" r" found at"
    )
    rogue_chars = [re.compile(r"\x1b\[16D\s+\x1b\[16D"), re.compile(r"\x1b\[42D\s+\x1b\[42D"), "\r"]

    spaces_rx = re.compile(r"^\s{42}|^\s{16}", re.DOTALL | re.MULTILINE)

    def clean_spaces(self, config):
        config = self.spaces_rx.sub("", config)
        return config
