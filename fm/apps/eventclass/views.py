# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.eventclass application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models import EventClass


class EventClassApplication(ExtDocApplication):
    """
    EventClass application
    """
    title = "Event Class"
    menu = "Setup | Event Classes"
    model = EventClass
    query_fields = ["name", "description"]
    query_condition = "icontains"

    @view(url=r"^(?P<id>[0-9a-f]{24})/json/", method=["GET"],
          access="read", api=True)
    def api_json(self, request, id):
        ec = self.get_object_or_404(EventClass, id=id)
        return ec.json
