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
    name="fm.event_priority_events"
    title="Event Priority Summary"
    requires_cursor=True
    columns=[
        Column("Event Priority"),
        Column("Events",align="RIGHT",summary="sum")]
    
    def get_queryset(self):
        return self.execute("""
            SELECT ep.name,COUNT(*)
            FROM fm_eventpriority ep JOIN fm_event e ON (ep.id=e.event_priority_id)
            GROUP BY 1
            ORDER BY 2 DESC""")

