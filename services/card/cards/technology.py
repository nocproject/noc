# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Technology card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from noc.inv.models.technology import Technology
from .base import BaseCard


class TechnologyCard(BaseCard):
    name = "technology"
    default_template_name = "technology"
    model = Technology

    def get_data(self):
        return {
            "object": self.object
        }
