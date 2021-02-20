# ---------------------------------------------------------------------
# Vendor: Allied Telesis
# OS:     AT8100
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# coded by azhur
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AlliedTelesis.AT8100"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+)> "
    pattern_prompt = r"^(?P<hostname>\S+)# "
    pattern_more = r"^--More--\s*"
    command_super = "enable"
    command_more = " "
    command_submit = "\r\n"
    username_submit = "\r"
    password_submit = "\r"
    command_disable_pager = "terminal length 0"
    command_exit = "exit"

    rx_interface_name = re.compile(r"^\d+\.\d+\.\d+$")

    def convert_interface_name(self, s):
        match = self.rx_interface_name.match(s)
        if match:
            return "port%s" % s
        return s

    INTERFACE_TYPES = {
        "port": "physical",
        "vlan": "SVI",
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:4])
