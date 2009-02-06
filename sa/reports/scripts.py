# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column
import noc.main.report
from noc.sa.models import script_registry

class Report(noc.main.report.Report):
    name="sa.scripts"
    title="Scripts"
    requires_cursor=False
    columns=[Column("Script"),Column("Interfaces")]
    
    def get_queryset(self):
        def get_interfaces(c):
            return ", ".join([i.__class__.__name__ for i in c.implements])
        return sorted([[n,get_interfaces(c)] for n,c in script_registry.classes.items()])
