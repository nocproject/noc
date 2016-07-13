# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Failed Scripts Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from sa.models.failedscriptlog import FailedScriptLog
from noc.core.translation import ugettext as _


class ReportObjectsSummary(SimpleReport):
    title = _("Failed Scripts")

    def get_data(self, **kwargs):
        data = [
            (
                r.timestamp,
                r.managed_object,
                r.address,
                r.script,
                r.error_code,
                r.error_text
            ) for r in FailedScriptLog.objects.order_by("-timestamp")[:100]
        ]
        return self.from_dataset(
            title=self.title,
            columns=[
                "Timestamp", "Managed Object", "Address",
                "Script", "Code", "Error"
            ],
            data=data)
