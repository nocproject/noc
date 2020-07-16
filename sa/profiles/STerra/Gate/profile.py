# ---------------------------------------------------------------------
# Vendor: STerra
# OS:     Gate
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "STerra.Gate"
    # to one SNMP GET request
    snmp_metrics_get_chunk = 2
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 3

    INTERFACE_TYPES = {
        1: "other",
        6: "physical",  # ethernetCsmacd
        24: "loopback",  # softwareLoopback
        0: "physical",  # gigabitEthernet
        53: "SVI",  # propVirtual
    }

    def get_interface_type(self, name):
        return self.INTERFACE_TYPES.get(name)
