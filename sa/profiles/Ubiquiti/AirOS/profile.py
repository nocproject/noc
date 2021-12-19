# ---------------------------------------------------------------------
# Vendor: Ubiquiti
# OS:     AirOS
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.snmp.render import render_mac


class Profile(BaseProfile):
    name = "Ubiquiti.AirOS"

    pattern_username = rb"([Uu][Bb][Nn][Tt] login|[Ll]ogin):"
    pattern_more = [(rb"CTRL\+C.+?a All", b"a")]
    pattern_prompt = rb"^\S+?(\.v(?P<version>\S+))?#"
    config_volatile = [r"^%.*?$"]

    snmp_display_hints = {"1.2.840.10036.2.1.1.1": render_mac}

    INTERFACE_TYPES = {
        1: "other",
        6: "physical",  # ethernetCsmacd
        24: "loopback",  # softwareLoopback
        53: "SVI",  # propVirtual
    }

    def get_interface_type(self, name):
        return self.INTERFACE_TYPES.get(name)
