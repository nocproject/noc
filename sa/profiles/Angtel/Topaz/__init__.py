# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Angtel (Angstrem telecom - http://www.angtel.ru/)
# OS:     Topaz
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Angtel.Topaz"
    pattern_unpriveleged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_prompt = r"^(?P<hostname>\S+)\s*#"
    pattern_syntax_error = r"% Unrecognized command|% Wrong number of parameters"
    command_super = "enable"
    command_disable_pager = "terminal datadump"
    pattern_more = "More: <space>,  Quit: q or CTRL+Z, One line: <return>"
    command_more = "a"
    command_exit = "exit"

    def setup_session(self, script):
        # Do not erase this.
        # Account, obtained through RADIUS required this.
        # v = script.cli("show privilege")
        # if ("15" not in v) and script.credentials["super_password"]:
        #    script.cli("enable\n%s" % script.credentials["super_password"])
        script.cli("show privilege")
