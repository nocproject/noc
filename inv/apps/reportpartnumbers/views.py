# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.reportpartnumbers
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow
from noc.inv.models.vendor import Vendor
from noc.inv.models.objectmodel import ObjectModel


class ReportPartnumbersApplication(SimpleReport):
    title = "Part Numbers"

    def get_data(self, **kwargs):
        data = []
        for v in Vendor.objects.order_by("name"):
            data += [SectionRow(name=v.name)]
            for m in ObjectModel.objects.filter(vendor=v.id):
                data += [[
                    m.get_data("asset", "part_no0"),
                    m.get_data("asset", "part_no1"),
                    m.get_data("asset", "part_no2"),
                    m.get_data("asset", "part_no3"),
                    m.get_data("asset", "asset_part_no0"),
                    m.get_data("asset", "asset_part_no1"),
                    m.get_data("asset", "asset_part_no2"),
                    m.get_data("asset", "asset_part_no3"),
                    m.name,
                    m.description
                ]]

        return self.from_dataset(
            title=self.title,
            columns=[
                "0", "1", "2", "3",
                "0", "1", "2", "3",
                "Name",
                "Description"
            ],
            data=data, enumerate=True
        )
