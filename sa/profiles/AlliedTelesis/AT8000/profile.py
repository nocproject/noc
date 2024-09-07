# ---------------------------------------------------------------------
# Vendor: Allied Telesis
# OS:     AT8000
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile
import re


class Profile(BaseProfile):
    name = "AlliedTelesis.AT8000"

    pattern_more = [
        (rb"^--More-- <Space> = next page, <CR> = one line, C = continuous, Q = quit", b"c")
    ]
    command_submit = b"\r\n"
    username_submit = b"\r"
    password_submit = b"\r"
    pattern_prompt = rb"^Manager::(?P<hostname>\S+)\$"

    rx_vlan = re.compile(
        r"^\s*VLAN Name\s*.+ (?P<name>\S+)\s*\n"
        r"^\s*VLAN ID\s*.+ (?P<vlan_id>\d+)\s*\n"
        r"^\s*Untagged Port\(s\)\s*.+ (?P<untagged>.+)\n"
        r"^\s*Tagged Port\(s\)\s*.+ (?P<tagged>.+)\n",
        re.MULTILINE,
    )

    def convert_interface_name(self, s):
        if s.startswith("Port "):
            return s[5:]
        return s

    @classmethod
    def get_interface_type(cls, name):
        if s.startswith("Ethernet"):
            return "physical"
