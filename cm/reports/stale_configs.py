# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column,BooleanColumn
import noc.main.report

class Report(noc.main.report.Report):
    name="cm.stale_configs"
    title="Stale Configs (2 days)"
    requires_cursor=True
    columns=[Column("Config"),Column("Last Pull")]
    
    def get_queryset(self):
        return self.execute("""
            SELECT repo_path,last_pull
            FROM cm_config WHERE last_pull IS NULL OR last_pull<('now'::timestamp-'2 days'::interval)
            ORDER BY 2
            """)
