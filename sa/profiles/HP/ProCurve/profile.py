# ---------------------------------------------------------------------
# Vendor: HP
# OS:     ProCurve
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "HP.ProCurve"

    pattern_username = rb"(Please Enter)?\s*(Login Name|Username):"
    pattern_password = rb"(Please Enter)?\s*Password:"
    pattern_prompt = rb"^[a-zA-Z0-9- _/.]+?(\(\S+\))?# "
    pattern_unprivileged_prompt = rb"^[a-zA-Z0-9- _/.]+?> "
    pattern_more = [
        (rb"Press any key to continue", b"\n"),
        (rb"-- MORE --, next page: Space, next line: Enter, quit: Control-C", b" "),
    ]
    pattern_syntax_error = rb"Invalid input: "
    command_disable_pager = "no page"
    command_super = b"enable"
    command_enter_config = "configure"
    command_leave_config = "exit"
    command_save_config = "write memory\n"
    command_exit = "exit"
    matchers = {"is_old_cli": {"caps": {"$in": ["HP | ProCurve | CLI | Old"]}}}

    #
    # Compare versions
    #
    # Version format is <letter>.<major>.<minor>[.<patch>]
    #
    rx_ver = re.compile(r"\d+")

    @classmethod
    def cmp_version(cls, v1, v2):
        if v1.count(".") != v2.count("."):
            return None
        l1 = v1.split(".", 1)
        l2 = v2.split(".", 1)
        if l1 != l2:
            # Different letters
            return None
        a = [int(z) for z in cls.rx_ver.findall(v1)]
        b = [int(z) for z in cls.rx_ver.findall(v2)]
        return (a > b) - (a < b)

    @classmethod
    def get_interface_type(cls, name):
        if name.lower().startswith("trk"):
            return "aggregated"
        elif name.lower().startswith("vlan"):
            return "SVI"
        elif name.lower().startswith("switch loopback"):
            return "loopback"
        return "physical"

    def convert_interface_name(self, s):
        return s
