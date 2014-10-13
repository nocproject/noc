# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.metric application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.extapplication import ExtApplication, view
from noc.pm.models.grafanadashboard import GrafanaDashboard


class GrafanaApplication(ExtApplication):
    """
    Metric application
    """
    title = "Grafana"

    @view("^(?P<idx>.+)/dashboard/(?P<name>.+)$", method=["PUT"],
          access="write", api=True)
    def api_save(self, request, idx, name):
        data = self.deserialize(request.raw_post_data)
        d = GrafanaDashboard.objects.filter(name=name).first()
        if not d:
            d = GrafanaDashboard(name=name)
        d.title = data["title"]
        d.tags = data["tags"]
        d.dashboard = data["dashboard"]
        d.save()
        return True

    @view("^(?P<idx>.+)/dashboard/(?P<name>.+)$", method=["GET"],
          access="read", api=True)
    def api_get(self, request, idx, name):
        d = self.get_object_or_404(GrafanaDashboard, name=name)
        return {
            "_source": {
                "dashboard": d.dashboard
            }
        }