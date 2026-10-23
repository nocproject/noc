# ----------------------------------------------------------------------
# Vendor: C3Solution
# OS:     PDU
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "C3Solution.PDU"

    INTERFACE_TYPES = {
        6: "physical",  # ethernetCsmacd
        24: "loopback",  # softwareLoopback
    }

    def get_interface_type(self, name):
        return self.INTERFACE_TYPES.get(name)
