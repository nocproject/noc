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

        port_types = []
        object_metrics = []
        context = {
            "port_types": port_types,
            "object_metrics": object_metrics,
            "device": self.object.name,
            "ip": self.object.address,
            "platform": self.object.platform or "Unknown platform",
            "device_id": self.object.id,
            "vendor": self.object.vendor or "Unknown platform"
        }

        MO_TEMPLATE_PATH = "templates/ddash/mo.j2"
        with open(MO_TEMPLATE_PATH) as f:
            CARD_TEMPLATE = Template(f.read())
        return CARD_TEMPLATE.render(context)