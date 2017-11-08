# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# TimePattern card handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.main.models.timepattern import TimePattern

# NOC modules
from base import BaseCard


class TimePatternCard(BaseCard):
    name = "timepattern"
    default_template_name = "timepattern"
    model = TimePattern
    default_title_template = "Time Pattern: {{ object.name }}"

    def get_data(self):
        return {
            "object": self.object,
            "terms": [t.term for t in self.object.timepatternterm_set.all()]
        }
