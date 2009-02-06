# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column,BooleanColumn
import noc.main.report

class Report(noc.main.report.MatrixReport):
    name="sa.objects_by_profiles_and_domains"
    title="Objects by Profile and Domains"
    requires_cursor=True
    
    def get_queryset(self):
        return self.execute("SELECT d.name,profile_name,COUNT(*) FROM sa_managedobject o JOIN sa_administrativedomain d ON (o.administrative_domain_id=d.id) GROUP BY 1,2")
