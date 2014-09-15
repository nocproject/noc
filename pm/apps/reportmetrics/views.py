# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pm.reportmetrics
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport
from noc.pm.probes.base import probe_registry


class ReportMetricsApplication(SimpleReport):
    title = "Metrics"

    def get_data(self, **kwargs):
        r = []
        for mt in probe_registry.probes:
            for hi in probe_registry.probes[mt]:
                r += [[
                    mt, hi.handler_name, hi.preference, hi.convert,
                    hi.scale, ", ".join(hi.req), ", ".join(hi.opt)
                ]]
        r = sorted(r, key=lambda x: (x[0], x[2]))
        return self.from_dataset(
            title=self.title,
            columns=["Metric Type", "Handler", "Preference",
                     "Convert", "Scale", "Required", "Optional"],
            data=r
        )
