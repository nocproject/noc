# ----------------------------------------------------------------------
# Prefix card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.ip.models.prefix import Prefix
from noc.ip.models.address import Address
from noc.inv.models.resourcepool import ResourcePool
from .base import BaseCard


class PrefixCard(BaseCard):
    name = "prefix"
    default_template_name = "prefix"
    model = Prefix

    SOURCES = {"M": "Manual", "i": "Interface", "w": "Whois", "n": "Neighbor"}

    def get_data(self):
        # Build upwards path
        path = []
        current = self.object.parent
        while current:
            path += [current]
            current = current.parent
        #
        return {
            "object": self.object,
            "source": self.SOURCES.get(self.object.source, "Unknown"),
            "path": reversed(path),
            "pools": list(ResourcePool.objects.filter()),
            "prefixes": list(Prefix.objects.filter(parent=self.object).order_by("prefix")),
            "addresses": list(Address.objects.filter(prefix=self.object).order_by("address")),
        }
