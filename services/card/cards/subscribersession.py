# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Subscriber Sessions Subcard
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseCard
from noc.inv.models.interface import Interface
from noc.inv.models.macvendor import MACVendor


class SubscriberSessionCard(BaseCard):
    name = "subscribersession"
    default_template_name = "subscribersession"
    model = Interface

    def get_data(self):
        macs = self.object.managed_object.scripts.get_mac_address_table(
            interface=self.object.name
        )
        if macs:
            for m in macs:
                m["mac_vendor"] = MACVendor.get_vendor(m["mac"]) or ""
        return {
            "macs": macs
        }
