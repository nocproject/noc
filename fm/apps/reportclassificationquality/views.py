# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Classification Quality Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport,TableColumn
##
##
##
class ReportClassificationQuality(SimpleReport):
    title="Classification Quality"
    def get_data(self,**kwargs):
        count=self.execute("SELECT COUNT(*) FROM fm_event")[0][0]
        classified=self.execute("""
            SELECT COUNT(*)
            FROM fm_event
            WHERE event_class_id NOT IN (
                    SELECT id FROM fm_eventclass
                    WHERE name IN ('DEFAULT','SNMP Trap','SYSLOG')
                    )
            """)[0][0]
        quality=classified*100/count if count else 100
        data=[
            ["Events",classified,count,quality],
        ]
        return self.from_dataset(title=self.title,
            columns=["",
                TableColumn("Classified",format="integer",align="right"),
                TableColumn("Total",format="integer",align="right"),
                TableColumn("Quality",format="percent",align="right")
                ],
            data=data)
