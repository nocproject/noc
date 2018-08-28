# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Prefix card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.ip.models.prefix import Prefix
from noc.ip.models.address import Address
from .base import BaseCard


class PrefixCard(BaseCard):
    name = "prefix"
    default_template_name = "prefix"
    model = Prefix

    SOURCES = {
        "M": "Manual",
        "i": "Interface",
        "w": "Whois",
        "n": "Neighbor"
    }

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
            "prefixes": list(Prefix.objects.filter(parent=self.object).order_by("prefix")),
            "addresses": list(Address.objects.filter(prefix=self.object).order_by("address")),
        }
