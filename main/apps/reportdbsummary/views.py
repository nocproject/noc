# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DB Summary Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport,TableColumn
##
##
##
class ReportreportDBSummary(SimpleReport):
    title="Database Summary"
    def get_data(self,**kwargs):
        return self.from_query(title=self.title,
            columns=["Table","Tablespace",
                TableColumn("Pages",align="right",format="integer",total="sum"),
                TableColumn("Records",align="right",format="integer",total="sum"),
                TableColumn("Size",align="right",format="size",total="sum")],
            query="""
            SELECT c.relname,t.spcname,c.relpages,c.reltuples,c.relpages*8192
            FROM pg_class c LEFT JOIN pg_tablespace t ON (t.oid=c.reltablespace)
            WHERE c.relkind='r' AND c.relname NOT LIKE 'pg_%%' AND c.relname NOT LIKE 'sql_%%'
            ORDER BY c.relpages DESC,c.reltuples DESC
            """)
