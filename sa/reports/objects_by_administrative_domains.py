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
    name="sa.objects_by_administrative_domains"
    title="Objects by Administrative Domains"
    requires_cursor=True
    columns=[Column("Domains"),Column("Qty",align="RIGHT",summary="sum")]
    
    def get_queryset(self):
        return self.execute("SELECT a.name,COUNT(*) FROM sa_managedobject o JOIN sa_administrativedomain a ON (o.administrative_domain_id=a.id) GROUP BY 1 ORDER BY 2 DESC")
