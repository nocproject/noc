# ---------------------------------------------------------------------
# Vendor: Cisco
# OS:     WLC
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Cisco.WLC"

    pattern_username = rb"^User:"
    pattern_more = [(rb"--More-- or \(q\)uit", b" ")]
    pattern_prompt = rb"^\(Cisco Controller\)\s+>"
    requires_netmask_conversion = True

    matchers = {"is_platform_5508": {"platform": {"$regex": r"AIR-CT5508.*"}}}

    INTERFACE_TYPES = {
        "Et": "physical",  # Ethernet
        "Fa": "physical",  # FastEthernet
        "Gi": "physical",  # GigabitEthernet
        "Lo": "loopback",  # Loopback
        "Tu": "tunnel",  # Tunnel
        "Tw": "physical",  # TwoGigabitEthernet or TwentyFiveGigE
        "Vi": "SVI",  # Virtual Interface
        "VL": "SVI",  # VLAN, found on C3500XL
        "Vl": "SVI",  # Vlan
    }

    @classmethod
    def get_interface_type(cls, name):
        return cls.INTERFACE_TYPES.get(name[:2])

    def convert_interface_name(self, interface):
        if interface.startswith("Virtual"):
            # Virtual Interface
            return "virtual"
        return self.convert_interface_name_cisco(interface)
