# ---------------------------------------------------------------------
# Vendor: Mellanox
# OS:     Cumulus
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Mellanox.Cumulus"
    pattern_username = rb"^[Ll]ogin: "
    pattern_more = [
        (rb"^lines \d+-\d+ ", b" "),
        (rb"^lines \d+-\d+/\d+ \(END\) ", b"\r"),
    ]
    pattern_prompt = rb"^\S+@(?P<hostname>\S+):~\$"
    pattern_syntax_error = rb"^% Unrecognized command \".+\"\."
    command_exit = "exit"
    command_disable_pager = "terminal length 999"
    config_volatile = [r"^## Generated at .+?\n"]

    #def convert_interface_name(self, s):
    #    s = s.replace("Ethernet ", "Eth")
    #    s = s.replace("port-channel ", "Po")
    #    s = s.replace("Vlan ", "vlan")
    #    return s
