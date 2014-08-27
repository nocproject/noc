# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.metricsettings application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.metricsettings import MetricSettings


class MetricSettingsApplication(ExtDocApplication):
    """
    MetricSettings application
    """
    title = "Metric Settings"
    model = MetricSettings

    @view("^(?P<settings_id>[0-9a-f]{24})/(?P<model_id>[^/]+)/(?P<object_id>[^/]+)/effective/trace/$",
          method=["GET"], access="read", api=True)
    def api_trace_effective(self, request, settings_id, model_id, object_id):
        s = self.get_object_or_404(MetricSettings, id=settings_id)
        o = MetricSettings(model_id=model_id, object_id=object_id).get_object()
        if not o:
            return self.response_not_found()
        r = []
        for es in MetricSettings.get_effective_settings(o, trace=True):
            r += [{
                "metric": es.metric,
                "metric_type": es.metric_type.name,
                "is_active": es.is_active,
                "storage_rule": es.storage_rule.name,
                "probe": es.probe.name,
                "interval": es.interval,
                "thresholds": es.thresholds,
                "handler": es.handler,
                "config": es.config,
                "errors": es.errors,
                "traces": es.traces
            }]
        return r
