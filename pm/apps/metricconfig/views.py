# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.metricconfig application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.metricconfig import MetricConfig


class MetricConfigApplication(ExtDocApplication):
    """
    MetricConfig application
    """
    title = "Metric Config"
    menu = "Setup | Metric Configs"
    model = MetricConfig
    query_fields = ["name", "description"]

    @view(url="^config/(?P<path>.+)$",
          url_name="static", access=True, api=True)
    def api_config_form(self, request, path):
        """
        Static file server
        """
        if not path.startswith("pm/probes/") and not path.startswith("solutions/"):
            return self.response_not_found()
        return self.render_static(request, path, document_root=".")
