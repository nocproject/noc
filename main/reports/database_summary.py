# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.database_summary
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.main.report import Column
import noc.main.report
import os

class Report(noc.main.report.Report):
    name="main.database_summary"
    title="Database Summary"
    requires_cursor=True
    columns=[
        Column("Table"),
        Column("Tablespace"),
        Column("Pages",align="RIGHT",summary="sum"),
        Column("Records",align="RIGHT",summary="sum"),
    ]
    
    def get_queryset(self):
        r=self.execute("""
        SELECT c.relname,t.spcname,c.relpages,c.reltuples
        FROM pg_class c LEFT JOIN pg_tablespace t ON (t.oid=c.reltablespace)
        WHERE c.relkind='r' AND c.relname NOT LIKE 'pg_%%' AND c.relname NOT LIKE 'sql_%%'
        ORDER BY c.relpages DESC,c.reltuples DESC
        """)
        return r
