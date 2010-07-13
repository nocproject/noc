# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIBs Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport,TableColumn
##
##
##
class ReportreportMIBs(SimpleReport):
    title="Installed MIBs"
    def get_data(self,**kwargs):
        return self.from_query(title=self.title,
            columns=[
                TableColumn("MIB",total_label="Total:"),
                TableColumn("Last Updated",format="date"),
                TableColumn("Uploaded",format="datetime"),
                TableColumn("Entries",align="right",format="integer",total="sum")],
            query="""SELECT m.name,m.last_updated,m.uploaded,COUNT(*)
            FROM fm_mib m JOIN fm_mibdata d ON (d.mib_id=m.id)
            GROUP BY 1,2,3
            ORDER BY 1 DESC""",
            enumerate=True)
