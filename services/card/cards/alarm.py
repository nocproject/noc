# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alarm card handler
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
import operator
## Third-party modules
from jinja2 import Template
## NOC modules
from base import BaseCard
from noc.fm.models.utils import get_alarm
from noc.inv.models.object import Object


class AlarmCard(BaseCard):
    default_template_name = "alarm"

    def dereference(self, id):
        return get_alarm(id)

    def get_data(self):
        now = datetime.datetime.now()
        # Get container path
        cp = []
        if self.object.managed_object.container:
            c = self.object.managed_object.container.id
            while c:
                try:
                    o = Object.objects.get(id=c)
                    # @todo: Address data
                    if o.container:
                        cp.insert(0, {
                            "id": o.id,
                            "name": o.name
                        })
                    c = o.container
                except Object.DoesNotExist:
                    break
        # Build result
        r = {
            "id": self.object.id,
            "alarm": self.object,
            "managed_object": self.object.managed_object,
            "timestamp": self.object.timestamp,
            "duration": now - self.object.timestamp,
            "subject": self.object.subject,
            "body": self.object.body,
            "container_path": cp
        }
        return r
