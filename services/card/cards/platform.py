# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Platform card
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from __future__ import absolute_import
# NOC modules
from noc.inv.models.platform import Platform
from .base import BaseCard


class PlatformCard(BaseCard):
    name = "platform"
    default_template_name = "platform"
    model = Platform

    def get_data(self):
        return {
            "object": self.object
        }
