# ---------------------------------------------------------------------
# Vendor: Eltex
# OS:     ESR
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Eltex.ESR"

    pattern_more = [
        (rb"^More: <space>,  Quit: q, One line: <return>$", b" "),
        (rb"^More\? Enter - next line; Space - next page; Q - quit; R - show the rest.", b"r"),
        (rb"\[Yes/press any key for no\]", b"Y"),
    ]
    pattern_unprivileged_prompt = rb"^\S+> "
    pattern_syntax_error = rb"^% (Unrecognized command|Incomplete command|Wrong number of parameters or invalid range, size or characters entered)$"
    command_disable_pager = "terminal datadump"
    command_super = b"enable"
    command_enter_config = "configure"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    pattern_prompt = rb"^\S+#"
    convert_interface_name = BaseProfile.convert_interface_name_cisco

    INTERFACE_TYPES = {
        6: "physical",
        161: "aggregated",
        54: "aggregated",
        53: "SVI",
        24: "loopback",
    }

    @classmethod
    def get_interface_type(cls, iftype):
        return cls.INTERFACE_TYPES.get(iftype)
