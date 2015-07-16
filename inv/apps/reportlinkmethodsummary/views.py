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
        data = db.noc.links.aggregate([
            {
                "$group": {
                    "_id": "$discovery_method",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}}
        ])
        data = [(x["_id"], x["count"]) for x in data["result"]]
        return self.from_dataset(
            title=self.title,
            columns=[
                "Method",
                TableColumn("Count", align="right",
                    format="integer", total="sum", total_label="Total")
            ],
            data=data,
            enumerate=True
        )
