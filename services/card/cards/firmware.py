# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Firmware card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.inv.models.firmware import Firmware
from .base import BaseCard


class FirmwarePlanCard(BaseCard):
    name = "firmware"
    default_template_name = "firmware"
    model = Firmware

    def get_data(self):
        return {
            "object": self.object
        }
