# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.reportappliedmetrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from collections import defaultdict
## NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow
from noc.pm.models.metricsettings import MetricSettings


class ReportAppliedMetricsApplication(SimpleReport):
    title = "Applied Metrics"

    def get_data(self, **kwargs):
        models = defaultdict(list)
        for ms in MetricSettings.objects.all():
            models[ms.model_id] += [[
                unicode(ms.get_object()),
                "; ".join(s.metric_set.name
                           for s in ms.metric_sets if s.is_active),
                "; ".join(s.metric_set.name
                           for s in ms.metric_sets if not s.is_active)
            ]]
        data = []
        for m in sorted(models):
            data += [SectionRow("Model: %s" % m)]
            data += sorted(models[m], key=lambda x: x[0])
        return self.from_dataset(
            title=self.title,
            columns=[
                "Object",
                "Active Metric Sets",
                "Inactive Metric Sets"
            ],
            data=data
        )
