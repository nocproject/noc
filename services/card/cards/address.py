# ----------------------------------------------------------------------
# Address card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.ip.models.address import Address
from .base import BaseCard


class AddressCard(BaseCard):
    name = "address"
    default_template_name = "address"
    model = Address

    SOURCES = {"M": "Manual", "i": "Interface", "m": "Management", "d": "DHCP", "n": "Neighbor"}

    def get_data(self):
        # Build upwards path
        path = []
        current = self.object.prefix
        while current:
            path += [current]
            current = current.parent
        return {
            "object": self.object,
            "path": reversed(path),
            "source": self.SOURCES.get(self.object.source, "Unknown"),
        }
