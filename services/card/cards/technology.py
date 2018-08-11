# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Technology card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from base import BaseCard
from noc.inv.models.technology import Technology


class TechnologyCard(BaseCard):
    name = "technology"
    default_template_name = "technology"
    model = Technology

    def get_data(self):
        return {
            "object": self.object
        }
