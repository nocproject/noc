# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.reportunknownsummary
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport, TableColumn
from noc.inv.models.unknownmodel import UnknownModel


class ReportUnknownModelsSummary(SimpleReport):
    title = "Unknown Models Summary"

    def get_data(self, **kwargs):
        data = {}  # vendor, part_no -> description, count
        for c in UnknownModel._get_collection().find():
            k = (c["vendor"], c["part_no"])
            if k in data:
                data[k][1] += 1
            else:
                data[k] = [c["description"], 1]
        data = sorted(
            ((k[0], k[1], data[k][0], data[k][1]) for k in data),
            key=lambda x: -x[3]
        )
        return self.from_dataset(
            title=self.title,
            columns=[
                "Vendor", "Part No", "Description",
                TableColumn("Count", format="numeric", align="right")
            ],
            data=data
        )
