# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# VRF card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.ip.models.vrf import VRF
from .base import BaseCard


class VRFCard(BaseCard):
    name = "vrf"
    default_template_name = "vrf"
    model = VRF

    def get_data(self):
        return {
            "object": self.object
        }
