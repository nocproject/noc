# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.metricsettings application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtDocApplication, view
from noc.pm.models.metricsettings import MetricSettings, MetricSettingsItem
from noc.pm.models.metricset import MetricSet
from noc.sa.interfaces.base import (DictListParameter, DocumentParameter,
                                    BooleanParameter)


class MetricSettingsApplication(ExtDocApplication):
    """
    MetricSettings application
    """
    title = "Metric Settings"
    model = MetricSettings

    @view("^(?P<model_id>[^/]+)/(?P<object_id>[^/]+)/settings/$",
          method=["GET"], access="read", api=True)
    def api_get_settings(self, request, model_id, object_id):
        o = MetricSettings.objects.filter(
            model_id=model_id, object_id=object_id).first()
        if o:
            return [
                {
                    "metric_set": str(ms.metric_set.id),
                    "metric_set__label": ms.metric_set.name,
                    "is_active": ms.is_active
                } for ms in o.metric_sets
            ]
        else:
            return []

    @view("^(?P<model_id>[^/]+)/(?P<object_id>[^/]+)/settings/$",
          method=["POST"], access="read", api=True,
          validate={
              "metric_sets": DictListParameter(attrs={
                  "metric_set": DocumentParameter(MetricSet),
                  "is_active": BooleanParameter()
              })
          }
    )
    def api_save_settings(self, request, model_id, object_id, metric_sets):
        def save_settings(o):
            o.save()
            return self.response({"status": True}, self.OK)

        o = MetricSettings.objects.filter(
            model_id=model_id, object_id=object_id).first()
        seen = set()
        mset = []
        for ms in metric_sets:
            if ms["metric_set"].id in seen:
                continue
            mset += [MetricSettingsItem(
                metric_set=ms["metric_set"],
                is_active=ms["is_active"]
            )]
            seen.add(ms["metric_set"].id)
        if o:
            o.metric_sets = mset
        else:
            o = MetricSettings(
                model_id=model_id,
                object_id=object_id,
                metric_sets=mset
            )
        self.submit_slow_op(request, save_settings, o)

    @view("^(?P<model_id>[^/]+)/(?P<object_id>[^/]+)/effective/trace/$",
          method=["GET"], access="read", api=True)
    def api_trace_effective(self, request, model_id, object_id):
        o = MetricSettings(model_id=model_id, object_id=object_id).get_object()
        if not o:
            return self.response_not_found()
        r = []
        for es in MetricSettings.get_effective_settings(o, trace=True, recursive=True):
            for m in es.metrics:
                r += [{
                    "metric": m.metric or None,
                    "metric_type": m.metric_type.name,
                    "is_active": es.is_active,
                    "probe": es.probe.name if es.probe else None,
                    "interval": es.interval if es.interval else None,
                    "thresholds": m.thresholds,
                    "handler": es.handler,
                    "config": es.config,
                    "errors": es.errors,
                    "traces": es.traces
                }]
        return r
