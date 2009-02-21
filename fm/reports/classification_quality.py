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
    name="fm.classification_quality"
    title="Event Classification Quality"
    requires_cursor=True
    columns=[
        Column(""),
        Column("Count",align="RIGHT")]
    
    def get_queryset(self):
        count=self.execute("SELECT COUNT(*) FROM fm_event")[0][0]
        classified=self.execute("""SELECT COUNT(*)
        FROM fm_event
        WHERE event_class_id NOT IN (
            SELECT id FROM fm_eventclass
            WHERE name IN ('DEFAULT','SNMP Trap','SYSLOG')
            )
        """)[0][0]
        if count==0:
            quality=100
        else:
            quality=classified*100/count
        return [
            ["Total events",count],
            ["Classified events",classified],
            ["Classification quality","%8.2f%%"%(quality)]
        ]

