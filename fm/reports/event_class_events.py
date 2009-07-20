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
    name="fm.event_class_events"
    title="Event Class Summary"
    requires_cursor=True
    columns=[
        Column("Event Class"),
        Column("Events",align="RIGHT",summary="sum")]
    
    def get_queryset(self):
        return self.execute("""
            SELECT ec.name,COUNT(*)
            FROM fm_eventclass ec JOIN fm_event e ON (ec.id=e.event_class_id)
            GROUP BY 1
            ORDER BY 2 DESC""")

