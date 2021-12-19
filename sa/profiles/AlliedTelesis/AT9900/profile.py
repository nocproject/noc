# ---------------------------------------------------------------------
# Vendor: Allied Telesis
# OS:     AT9900
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AlliedTelesis.AT9900"

    pattern_username = rb"^.*\slogin: "
    pattern_more = [(rb"^--More--.*", b"c")]
    command_submit = b"\r"
    command_save_config = "create config=boot1.cfg"
    pattern_prompt = r"^Manager.*>"
    convert_mac = BaseProfile.convert_mac_to_dashed

    def convert_interface_name(self, s):
        if s.startswith("Port "):
            return s[5:]
        return s

    INTERFACE_TYPES = {
        "eth": "physical",
        "por": "physical",
        "loo": "loopback",  # Loopback
        "vla": "SVI",  # vlan
        "un": "unknown",
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:3].lower())
