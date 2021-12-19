# ---------------------------------------------------------------------
# Vendor: Upvel
# OS:     UP
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Upvel.UP"

    pattern_unprivileged_prompt = rb"^(?P<hostname>\S+)\s*>"
    pattern_prompt = rb"^(?P<hostname>\S+)\s*(\((config|config-\S+)\)|)\s*#"
    pattern_syntax_error = rb"\n% (Invalid|Ambiguous) word detected at"
    command_super = "enable"
    command_disable_pager = "terminal length 0"
    command_submit = b"\r\n"
    username_submit = b"\r\n"
    password_submit = b"\r\n"
    pattern_more = [(rb"-- more --, next page: Space, continue: g, quit: ^", b"g")]
    command_enter_config = "configure terminal"
    command_leave_config = "end"
    command_save_config = "copy running-config startup-config"
    command_exit = "logout"

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("Gi 1/3")
        'GigabitEthernet 1/3'
        >>> Profile().convert_interface_name("2.5G 1/2")
        '2.5GigabitEthernet 1/2'
        >>> Profile().convert_interface_name("10G 1/1")
        '10GigabitEthernet 1/1'
        """
        s = s.strip()
        if s.startswith("Gi "):
            return "GigabitEthernet %s" % s[3:].strip()
        if s.startswith("2.5G "):
            return "2.5GigabitEthernet %s" % s[5:].strip()
        if s.startswith("10G G "):
            return "10GigabitEthernet %s" % s[4:].strip()
        return s

    def get_interface_names(self, name):
        """
        LLDP port format is number: 1, 17 etc...
        :param name:
        :return:
        """

        return [
            "GigabitEthernet 1/%s" % name,
            "2.5GigabitEthernet 1/%s" % name,
            "10GigabitEthernet 1/%s" % name,
        ]

    INTERFACE_TYPES = {
        "Gi": "physical",  # GigabitEthernet
        "2.": "physical",  # 2.5GigabitEthernet
        "10": "physical",  # 10GigabitEthernet
        "VL": "SVI",  # VLAN
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])
