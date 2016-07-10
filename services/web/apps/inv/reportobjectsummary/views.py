# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.reportobjectsummary
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.inv.models.object import Object
from noc.inv.models.objectmodel import ObjectModel


class ReportObjectSummaryApplication(SimpleReport):
    title = "Object Summary"

    def get_data(self, **kwargs):
        self.model_name = {}  # oid -> name
        data = Object._get_collection().aggregate([
            {
                "$group": {
                    "_id": "$model",
                    "total": {
                        "$sum": 1
                    }
                }
            }
        ])
        oms = [x["_id"] for x in data["result"] if x["_id"]]
        c = ObjectModel._get_collection()
        om_names = {}
        while oms:
            chunk, oms = oms[:500], oms[500:]
            om_names.update(
                dict(
                    (x["_id"], x["name"])
                    for x in c.find({
                        "_id": {
                            "$in": chunk
                        }
                    }, {
                        "_id": 1,
                        "name": 1
                    })
                )
            )
        data = sorted((
            [om_names[x["_id"]], x["total"]]
            for x in data["result"]
            if x["_id"] in om_names
        ), key=lambda x: -x[1])
        return self.from_dataset(
            title=self.title,
            columns=[
                "Model",
                TableColumn("Count", format="numeric",
                            align="right", total="sum")
            ],
            data=data,
            enumerate=True
        )
