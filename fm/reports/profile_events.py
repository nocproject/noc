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
    name="fm.profile_events"
    title="Profile Summary"
    requires_cursor=True
    columns=[
        Column("Profile"),
        Column("Events",align="RIGHT",summary="sum")]
    
    def get_queryset(self):
        return self.execute("""
            SELECT mo.profile_name,COUNT(*)
            FROM fm_event e JOIN sa_managedobject mo ON (e.managed_object_id=mo.id)
            GROUP BY 1
            ORDER BY 2 DESC""")

