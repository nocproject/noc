# ---------------------------------------------------------------------
# Vendor: VmWare
# OS:     ESXi
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "OS.ESXi"

    # pattern_username = "^((?!Last)\S+ login|[Ll]ogin):"
    pattern_unprivileged_prompt = rb"^([\w\~\-\.\/]*\s+)\$\s*"
    pattern_prompt = rb"^([\w\~\-\.\/]*\s+)#\s*"
    pattern_syntax_error = (
        rb"^(-\w+: \w+: not found|-\w+: \w+: No such file or directory"
        rb"|\w+: \w+: command not found"
        rb"|\w+: \w+: \w+: No such file or directory)"
    )
    command_disable_pager = "export LANG=en_GB.UTF-8"
    # command_super = "su"
    command_exit = "exit"
    pattern_more = [(rb"--More--", b"\n")]

    INTERFACE_TYPES = {
        1: "other",
        6: "physical",  # ethernetCsmacd
        24: "loopback",  # softwareLoopback
        258: "SVI",  # propVirtual
        54: "physical",  # propMultiplexor
        161: "aggregated",  # ieee8023adLag
        53: "SVI",  # propVirtual
    }

    def get_interface_type(self, name):
        return self.INTERFACE_TYPES.get(name)
