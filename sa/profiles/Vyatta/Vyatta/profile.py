# ---------------------------------------------------------------------
# Vendor: Vyatta
# OS:     Vyatta
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Vyatta.Vyatta"

    pattern_username = rb"[Ll]ogin: (?!\S+)"
    pattern_prompt = rb"^(?P<username>\S+)@(?P<hostname>\S+):[^$]+\$ "
    pattern_more = [(rb"^:", b" "), (rb"\[confirm\]", b"\n")]
    command_disable_pager = "set terminal length 0"
    command_enter_config = "configure"
    command_leave_config = "commit\nexit"

    @classmethod
    def get_interface_type(cls, name):
        if name.startswith("eth"):
            return "physical"
        if name.startswith("lo"):
            return "loopback"
        if name.startswith("br"):
            return "aggregated"
        if name.startswith("vtun"):
            return "tunnel"
        raise Exception("Cannot detect interface type for %s" % name)
