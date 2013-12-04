# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.reportcompare
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app.simplereport import SimpleReport, SectionRow
from noc.inv.models.vendor import Vendor
from noc.inv.models.objectmodel import ObjectModel


class ReportCompareApplication(SimpleReport):
    title = "Compare Specs"

    def get_data(self, **kwargs):
        data = []
        for v in Vendor.objects.order_by("name"):
            vd = []
            for m in ObjectModel.objects.filter(
                    vendor=v.id, data__management__managed=True):
                vd += [(
                    m.name,
                    m.get_data("dimensions", "width") or "",
                    m.get_data("dimensions", "height") or "",
                    m.get_data("dimensions", "depth") or "",
                    m.get_data("rackmount", "units") or ""
                )]
            if vd:
                data += [SectionRow(name=v.name)]
                data += vd

        return self.from_dataset(
            title=self.title,
            columns=[
                "Model", "W", "H", "D", "RU"
            ],
            data=data, enumerate=True
        )
