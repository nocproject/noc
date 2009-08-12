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
    name="fm.unclassified_trap_oids"
    title="Unclassified Trap OIDs"
    requires_cursor=True
    columns=[
        Column("OID"),
        Column("Name"),
        Column("Count",align="RIGHT")]
    
    def get_queryset(self):
        from noc.fm.models import MIB
        return [(x[0],MIB.get_name(x[0]),x[1]) for x in self.execute("""
            SELECT ed.value,COUNT(*)
            FROM fm_eventdata ed JOIN fm_event e ON (e.id=ed.event_id)
            WHERE ed.key='1.3.6.1.6.3.1.1.4.1.0'
                AND e.event_class_id IN (
                    SELECT id FROM fm_eventclass
                    WHERE name IN ('DEFAULT','SNMP Trap')
                    )
            GROUP BY 1
            ORDER BY 2 DESC""")]

