# ---------------------------------------------------------------------
# NSGATE.NIS
# Dumb profile to allow managed object creating
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NSGATE.NIS"

    INTERFACE_TYPES = {
        6: "physical",  # ethernetCsmacd
        24: "loopback",  # softwareLoopback
        136: "SVI",
        161: "aggregated",
    }

    def get_interface_type(self, name):
        return self.INTERFACE_TYPES.get(name)

    def convert_interface_name(self, interface):
        if interface.startswith("Link Aggregations"):
            return f"Po {interface[-1]}"
        elif interface.startswith("2.5"):
            return f"Tw{interface.split()[-1]}"
        return self.convert_interface_name_cisco(interface)
