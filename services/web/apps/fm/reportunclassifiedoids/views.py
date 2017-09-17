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

    def get_data(self, **kwargs):
        c = EventClass.objects.filter(name="Unknown | SNMP Trap").first()
        pipeline = [{"$match": {"event_class": c.id}},
                    {"$project": {"vars": 1}},
                    {"$group": {"_id": "$vars.trap_oid", "count": {"$sum": 1}}}]
        oids = ActiveEvent._get_collection().aggregate(pipeline)
        data = [(e["_id"], MIB.get_name(e["_id"]), e["count"]) for e in oids]
        data = sorted(data, key=lambda x: -x[2])
        return self.from_dataset(title=self.title,
                                 columns=["OID", "Name",
                                          TableColumn("Count", format="integer",
                                                      align="right", total="sum")],
                                 data=data)
