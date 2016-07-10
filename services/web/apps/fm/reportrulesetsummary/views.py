# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ruleset Summary Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.fm.models import (AlarmClass, EventClass,
                           EventClassificationRule)
from noc.lib.collection import Collection


class ReportRulesetSummary(SimpleReport):
    title = "Ruleset Summary"

    def get_data(self, **kwargs):
        def get_count(cn, m):
            collection = Collection(cn, m)
            collection.load()
            total = m.objects.count()
            builtin = len(collection.items)
            local = total - builtin
            return [builtin, local, total]

        data = [
            ["Alarm Classes"] + get_count("fm.alarmclasses", AlarmClass),
            ["Event Classies"] + get_count("fm.eventclasses", EventClass),
            ["Classification Rules"] + get_count("fm.eventclassificationrules", EventClassificationRule)
        ]

        return self.from_dataset(
            title=self.title,
            columns=[
                "",
                TableColumn("Builtin", align="right", format="integer"),
                TableColumn("Local", align="right", format="integer"),
                TableColumn("Total", align="right", format="integer")
            ],
            data=data)
