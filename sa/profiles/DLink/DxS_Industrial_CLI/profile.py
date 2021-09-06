# ---------------------------------------------------------------------
# Vendor: DLink
# OS:     DxS_Industrial_CLI
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DLink.DxS_Industrial_CLI"
    pattern_more = r"CTRL\+C.+?a A[Ll][Ll]\s*"
    pattern_unprivileged_prompt = r"^(?P<hostname>\S+?)>"
    pattern_prompt = r"^(?P<hostname>\S+?)#"
    pattern_syntax_error = r"% Invalid input detected at"
    command_disable_pager = "terminal length 0"
    command_more = "a"
    command_super = "enable"
    command_enter_config = "configure terminal"
    command_leave_config = "exit"
    command_save_config = "copy running-config startup-config\n"
    command_exit = "logout"

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("eth1/0/1")
        'Eth1/0/1'
        >>> Profile().convert_interface_name("1/1")
        'Eth1/0/1'
        >>> Profile().convert_interface_name("port-channel 1")
        'Port-channel1'
        >>> Profile().convert_interface_name("mgmt_ipif 0")
        'mgmt_ipif0'
        """
        s = s.replace(" ", "")
        if s.startswith("eth"):
            return "E%s" % s[1:]
        elif s.startswith("1/"):
            return "Eth1/0/%s" % s[2:]
        elif s.startswith("port-channel"):
            return "P%s" % s[1:]
        else:
            return s

    INTERFACE_TYPES = {
        "eth": "physical",
        "vla": "SVI",  # vlan
        "mgm": "management",  # mgmt_ipif
        "por": "aggregated",  # Port-channel
        "nul": "null",  # null
        "loo": "loopback",  # loopback
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get((name[:3]).lower())
