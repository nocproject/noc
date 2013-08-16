# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## fm.classificationrule application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.fm.models import EventClassificationRule


class EventClassificationRuleApplication(ExtDocApplication):
    """
    EventClassificationRule application
    """
    title = "Classification Rule"
    menu = "Setup | Classification Rules"
    model = EventClassificationRule
    query_condition = "icontains"

    @view(url=r"^(?P<id>[a-z0-9]{24})/json/$", method=["GET"], api=True,
          access="read")
    def api_json(self, request, id):
        rule = self.get_object_or_404(EventClassificationRule, id=id)
        return rule.to_json()
