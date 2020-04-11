# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Platform card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.inv.models.platform import Platform
from .base import BaseCard


class PlatformCard(BaseCard):
    name = "platform"
    default_template_name = "platform"
    model = Platform

    def get_data(self):
        return {"object": self.object}
