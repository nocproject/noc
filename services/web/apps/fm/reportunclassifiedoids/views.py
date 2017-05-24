# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Unclassified OIDS Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.fm.models.activeevent import ActiveEvent
from noc.fm.models.eventclass import EventClass
from noc.fm.models.mib import MIB
from noc.core.translation import ugettext as _


class ReportUnclassifiedOIDs(SimpleReport):
    title = _("Unclassified Trap OIDs")

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

    def get_data(self, **kwargs):
        c = EventClass.objects.filter(name="Unknown | SNMP Trap").first()
        oids = ActiveEvent.objects.filter(event_class=c.id).exec_js(self.c_f)
        data = [(o, MIB.get_name(o), c) for o, c in oids.items()]
        data = sorted(data, key=lambda x: -x[2])
        return self.from_dataset(title=self.title,
            columns=["OID", "Name",
                     TableColumn("Count", format="integer",
                                 align="right", total="sum")],
            data=data)
