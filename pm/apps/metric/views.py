# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.metric application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.metric import Metric
from noc.pm.db.base import tsdb


class MetricApplication(ExtDocApplication):
    """
    Metric application
    """
    title = "Metric"
    menu = "Setup | Metrics"
    model = Metric
    query_fields = ["name__icontains"]
    glyph = "line-chart"

    @view("^find/$", method=["GET"], access="read", api=True)
    def api_graphite_find(self, request):
        query = request.GET.get("query")
        metrics = []
        seen = set()
        for m in tsdb.find_detail(query):
            name = m.name.split(".")[-1]
            if name in seen:
                continue
            seen.add(name)
            is_leaf = not m.has_children
            metrics += [{
                "leaf": 1 if is_leaf else 0,
                "text": name,
                "id": m,
                "allowChildren": 0 if is_leaf else 1,
                "context": {},
                "expandable": 0 if is_leaf else 1
            }]
        return metrics
