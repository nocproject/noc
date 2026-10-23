# ---------------------------------------------------------------------
# Vendor: Mellanox
# OS:     Onyx
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Mellanox.Onyx"
    pattern_username = rb"^[Ll]ogin: "
    pattern_more = [
        (rb"^lines \d+-\d+ ", b" "),
        (rb"^lines \d+-\d+/\d+ \(END\) ", b"\r"),
    ]
    pattern_unprivileged_prompt = rb"^\S+ \[.+\] > "
    pattern_prompt = rb"^(?:\x00)?(?P<hostname>\S+) \[.+\] # "
    command_super = b"enable"
    pattern_syntax_error = rb"^% Unrecognized command \".+\"\."
    command_exit = "exit"
    command_disable_pager = "terminal length 999"
    config_volatile = [r"^## Generated at .+?\n"]

    def convert_interface_name(self, s):
        s = s.replace("Ethernet ", "Eth")
        s = s.replace("port-channel ", "Po")
        return s.replace("Vlan ", "vlan")
