# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.reportlinkmethodsummary
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.lib.nosql import get_db


class reportlinkmethodsummaryApplication(SimpleReport):
    title = "Link Method Summary"

    def get_data(self, **kwargs):
        db = get_db()
        data = db.noc.links.group(
            key={"discovery_method": True},
            condition={}, initial={"count": 0},
            reduce="function(doc, prev) {prev.count += 1;}"
        )
        data = [(r["discovery_method"], int(r["count"])) for r in data]
        data = sorted(data, key=lambda x: -x[1])
        return self.from_dataset(
            title=self.title,
            columns=[
                "Method",
                TableColumn("Count", align="right",
                    format="integer", total="sum", total_label="Total")
            ],
            data=data
        )
