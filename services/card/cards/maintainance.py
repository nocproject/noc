# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Maintainance card handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## Third-party modules
import jinja2
## NOC modules
from base import BaseCard
from noc.maintainance.models.maintainance import Maintainance


class MaintainanceCard(BaseCard):
    default_template_name = "maintainance"
    model = Maintainance
    default_title_template = "Maintainance: {{ object.subject }}"

    def get_data(self):
        stpl = self.object.type.card_template or self.default_title_template
        now = datetime.datetime.now()
        if self.object.start > now:
            status = "before"
        elif self.object.is_completed:
            status = "complete"
        else:
            status = "progress"
        return {
            "title": jinja2.Template(stpl).render({"object": self.object}),
            "object": self.object,
            "subject": self.object.subject,
            "contacts": self.object.contacts,
            "start": self.object.start,
            "stop": self.object.stop,
            "description": self.object.description,
            "status": status
        }
