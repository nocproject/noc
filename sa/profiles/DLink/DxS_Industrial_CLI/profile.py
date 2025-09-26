# ---------------------------------------------------------------------
# Vendor: DLink
# OS:     DxS_Industrial_CLI
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "DLink.DxS_Industrial_CLI"

    pattern_more = [(rb"CTRL\+C.+?a A[Ll][Ll]\s*", b"a")]
    pattern_more = [
        (rb"CTRL\+C.+?a A[Ll][Ll]\s*", b"a"),
        (
            rb"Destination filename startup-config\? \[y\/n\]",
            b"y",
        ),
    ]
    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+?)>"
    pattern_prompt = rb"^(?P<hostname>\S+?)(?:\(config\))?#"
    pattern_syntax_error = rb"% Invalid input detected at"
    command_disable_pager = "terminal length 0"
    command_super = b"enable"
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
        if s.startswith("1/"):
            return "Eth1/0/%s" % s[2:]
        if s.startswith("port-channel"):
            return "P%s" % s[1:]
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
