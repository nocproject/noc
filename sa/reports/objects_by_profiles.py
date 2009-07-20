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
    name="sa.objects_by_profiles"
    title="Objects by Profiles"
    requires_cursor=True
    columns=[Column("Profile"),Column("Qty",align="RIGHT",summary="sum")]
    
    def get_queryset(self):
        return self.execute("SELECT profile_name,COUNT(*) FROM sa_managedobject GROUP BY 1 ORDER BY 2 DESC")
