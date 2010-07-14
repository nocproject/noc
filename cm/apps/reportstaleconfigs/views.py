# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Stale Configs Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport,TableColumn
## Interval in days to consider config stale
STALE_INTERVAL=2
##
##
##
class Reportreportstaleconfigs(SimpleReport):
    title="Stale Configs (for %d days)"%STALE_INTERVAL
    def get_data(self,**kwargs):
        return self.from_query(title=self.title,
            columns=["Config",TableColumn("Last Pull",format="datetime")],
            query="""
                SELECT repo_path,last_pull
                FROM cm_config WHERE last_pull IS NULL OR last_pull<('now'::timestamp-'%d days'::interval)
                ORDER BY 2
            """%STALE_INTERVAL,
            enumerate=True)
