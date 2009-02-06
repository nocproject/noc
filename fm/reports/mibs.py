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
    name="fm.mibs"
    title="Loaded MIBs"
    requires_cursor=True
    columns=[
        Column("MIB"),
        Column("Last Updated"),
        Column("Uploaded"),
        Column("Count")]
    
    def get_queryset(self):
        return self.execute("""
            SELECT m.name,m.last_updated,m.uploaded,COUNT(*)
            FROM fm_mib m JOIN fm_mibdata d ON (d.mib_id=m.id)
            GROUP BY 1,2,3
            ORDER BY 1 DESC""")
