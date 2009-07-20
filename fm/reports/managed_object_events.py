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
    name="fm.managed_object_events"
    title="Managed Object Summary"
    requires_cursor=True
    columns=[
        Column("Managed Object"),
        Column("Events",align="RIGHT",summary="sum")]
    
    def get_queryset(self):
        return self.execute("""
            SELECT mo.name,COUNT(*)
            FROM fm_event e JOIN sa_managedobject mo ON (e.managed_object_id=mo.id)
            GROUP BY 1
            ORDER BY 2 DESC""")

