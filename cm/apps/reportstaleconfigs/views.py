# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Stale Configs Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.cm.models import Config


class ReportStaleConfig(SimpleReport):
    title = "Stale Configs"

    def get_data(self, **kwargs):
        return self.from_dataset(title=self.title,
            columns=["Config", TableColumn("Last Pull", format="datetime")],
            data=[(c.repo_path, c.last_pull) for c
                  in Config.objects.all()
                  if c.is_stale])
