# ---------------------------------------------------------------------
# Vendor: Fortinet
# OS:     FortiOS v4.X
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Fortinet.Fortigate"

    pattern_more = [(rb"^--More--", b" ")]
    pattern_prompt = rb"b^\S+\ [#\$]"

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
