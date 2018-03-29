# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Angtel (Angstrem telecom - http://www.angtel.ru/)
# OS:     Topaz
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Angtel.Topaz"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)\s*>"
    pattern_prompt = r"^(?P<hostname>\S+)\s*(?:\(config[^\)]*\))?#"
    pattern_syntax_error = r"% Unrecognized command|% Wrong number of parameters"
    command_super = "enable"
    command_disable_pager = "terminal datadump"
    pattern_more = [(r"More: <space>,  Quit: q or CTRL+Z, One line: <return>", "a"),
                    (r"^Overwrite file \[\S+\]\.+\s*\(Y/N\).+", "Y\n")]
    command_exit = "exit"
    convert_interface_name = BaseProfile.convert_interface_name_cisco

    def setup_session(self, script):
        # Do not erase this.
        # Account, obtained through RADIUS required this.
        # v = script.cli("show privilege")
        # if ("15" not in v) and script.credentials["super_password"]:
        #    script.cli("enable\n%s" % script.credentials["super_password"])
        script.cli("show privilege")
