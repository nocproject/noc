# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Unclassified OIDS Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.lib.app.simplereport import SimpleReport,TableColumn
from noc.fm.models import MIB
##
##
##
class ReportUnclassifiedOIDs(SimpleReport):
    title="Unclassified Trap OIDs"
    def get_data(self,**kwargs):
        data=[(x[0],MIB.get_name(x[0]),x[1]) for x in self.execute("""
            SELECT ed.value,COUNT(*)
            FROM fm_eventdata ed JOIN fm_event e ON (e.id=ed.event_id)
            WHERE ed.key='1.3.6.1.6.3.1.1.4.1.0'
                AND e.event_class_id IN (
                    SELECT id FROM fm_eventclass
                    WHERE name IN ('DEFAULT','SNMP Trap')
                    )
            GROUP BY 1
            ORDER BY 2 DESC""")]
        return self.from_dataset(title=self.title,
            columns=["OID","Name",TableColumn("Count",format="numeric",align="right",total="sum")],
            data=data)
