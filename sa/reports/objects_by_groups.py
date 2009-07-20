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
    name="sa.config_by_group"
    title="Configs by Groups"
    requires_cursor=True
    columns=[Column("Group"),Column("Qty",align="RIGHT",summary="sum")]
    
    def get_queryset(self):
        return self.execute("""
            SELECT g.name,COUNT(*)
            FROM sa_managedobject o
                JOIN sa_managedobject_groups og ON (o.id=og.managedobject_id)
                JOIN sa_objectgroup g ON (og.objectgroup_id=g.id)
            GROUP BY 1 ORDER BY 2 DESC""")
