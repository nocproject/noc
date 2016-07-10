# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Missed MIBs Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.fm.models import MIB, ActiveEvent, EventClass, MIB


class ReportMissedMIBs(SimpleReport):
    title = "Missed MIBs"

    c_f = """
    function() {
        var c = {}
        db[collection].find(query, {"vars": 1}).forEach(function(doc) {
            var oid = doc.vars.trap_oid;
            c[oid] = (c[oid] || 0) + 1;
        });
        return c;
    }
    """

    rx_unclassified = re.compile(r"\.\d+$")
    
    def get_data(self, **kwargs):
        c = EventClass.objects.filter(name="Unknown | SNMP Trap").first()
        oids = ActiveEvent.objects.filter(event_class=c.id).exec_js(self.c_f)
        d = [(o, MIB.get_name(o), c) for o, c in oids.items()]
        data = [(o, n, c) for o, n, c in d
                if self.rx_unclassified.search(n)]
        return self.from_dataset(title=self.title,
            columns=["OID", "Name",
                     TableColumn("Count", format="integer",
                                 align="right", total="sum")],
            data=data)
