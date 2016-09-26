# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ManagedObject's dynamic dashboard
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.models.managedobject import ManagedObject
from base import BaseDashboard
from noc.inv.models.interface import Interface
from noc.lib.text import split_alnum
from noc.pm.models.metrictype import MetricType
from jinja2 import Template

class MODashboard(BaseDashboard):
    name = "mo"

    def resolve_object(self, object):
        try:
            return ManagedObject.objects.get(id=object)
        except ManagedObject.DoesNotExist:
            raise self.NotFound()

    def render(self):
        def interface_profile_has_metrics(profile):
            """
            Check interface profile has metrics
            """
            for m in profile.metrics:
                if m.is_active and m.metric_type.name in (
                        "Interface | Load | In",
                        "Interface | Load | Out"
                ):
                    return True
            return False

        context = {
            "title": self.object.name
        }

        MO_TEMPLATE_PATH = "templates/ddash/mo.j2"
        with open(MO_TEMPLATE_PATH) as f:
            CARD_TEMPLATE = Template(f.read())
        return CARD_TEMPLATE.render(context)