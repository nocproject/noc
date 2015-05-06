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
                    vendor=v.id, data__management__managed=True).order_by("name"):
                ru = m.get_data("rackmount", "units")
                if ru:
                    ru = "%sU" % ru
                else:
                    ru = ""
                weight = m.get_data("weight", "weight")
                if weight:
                    weight = str(weight)
                    if m.get_data("weight", "is_recursive"):
                        weight += "+"
                else:
                    weight = ""
                vd += [(
                    m.name,
                    m.get_data("dimensions", "width") or "",
                    m.get_data("dimensions", "height") or "",
                    m.get_data("dimensions", "depth") or "",
                    ru,
                    weight
                )]
            if vd:
                data += [SectionRow(name=v.name)]
                data += vd

        return self.from_dataset(
            title=self.title,
            columns=[
                "Model", "W", "H", "D", "RU", "Weight (kg)"
            ],
            data=data, enumerate=True
        )
