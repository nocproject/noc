# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.grafana application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.pm.models.grafanadashboard import GrafanaDashboard


class GrafanaApplication(ExtApplication):
    """
    Metric application
    """
    title = "Grafana"

    @view("^noc/dashboard/(?P<name>.+)$", method=["POST"],
          access="read", api=True)
    def api_dashboard_search(self, request, name):
        if name != "_search":
            return self.response_not_found()
        data = self.deserialize(request.raw_post_data)
        limit = data.get("size", 20)
        q = data["query"]["query_string"]["query"]
        qs = {}
        if q.startswith("title:"):
            r = "^" + q[6:].replace("*", ".*")
            qs = {"title": re.compile(r, re.IGNORECASE)}
        elif q.startswith("tags:"):
            qs = {"tags", q[5:]}
        result = []
        for d in GrafanaDashboard.objects.filter(**qs)[:limit]:
            result += [{
                "_id": d.name,
                "_source": {
                    "title": d.title,
                    "tags": d.tags
                }
            }]
        return {
            "hits": {
                "hits": result
            },
            "facets": {
                "tags": {
                    "terms": []
                }
            }
        }

    @view("^noc/dashboard/(?P<name>.+)$", method=["PUT"],
          access="write", api=True)
    def api_save(self, request, name):
        data = self.deserialize(request.raw_post_data)
        d = GrafanaDashboard.objects.filter(name=name).first()
        if not d:
            d = GrafanaDashboard(name=name)
        d.title = data["title"]
        d.tags = data["tags"]
        d.dashboard = data["dashboard"]
        d.save()
        return True

    @view("^noc/dashboard/(?P<name>.+)$", method=["GET"],
          access="read", api=True)
    def api_get(self, request, name):
        d = self.get_object_or_404(GrafanaDashboard, name=name)
        return {
            "_source": {
                "dashboard": d.dashboard
            }
        }

    @view("^noc/dashboard/(?P<name>.+)$", method=["DELETE"],
          access="write", api=True)
    def api_delete(self, request, name):
        d = self.get_object_or_404(GrafanaDashboard, name=name)
        d.delete()
        return True
