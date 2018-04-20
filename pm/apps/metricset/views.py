# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.metricset application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.metricset import MetricSet


class MetricSetApplication(ExtDocApplication):
    """
    MetricSet application
    """
    title = "Metric Set"
    menu = "Setup | Metric Sets"
    model = MetricSet
    query_fields = ["name", "description"]

    @view(url="^(?P<metricset_id>[0-9a-f]{24})/effective/$",
          method=["GET"], access="read", api=True)
    def api_effective(self, request, metricset_id):
        ms = self.get_object_or_404(MetricSet, id=metricset_id)
        return [
            {
                "metric_type_name": m.metric_type.name,
                "metric_type_id": str(m.metric_type.id),
                "is_active": m.is_active,
                "low_error": m.low_error,
                "low_warn": m.low_warn,
                "high_warn": m.high_warn,
                "high_error": m.high_error,
                "description": m.metric_type.description
            } for m in ms.get_effective_metrics()
        ]
