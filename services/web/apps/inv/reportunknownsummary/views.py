# ---------------------------------------------------------------------
# inv.reportunknownsummary
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.services.web.base.simplereport import SimpleReport, TableColumn
from noc.inv.models.unknownmodel import UnknownModel
from noc.core.translation import ugettext as _


class ReportUnknownModelsSummary(SimpleReport):
    title = _("Unknown Models Summary")

    def get_data(self, **kwargs):
        data = {}  # vendor, part_no -> description, count
        for c in UnknownModel._get_collection().find():
            vendor = c["vendor"]
            if isinstance(c["vendor"], list):
                # Fix for bad vendor code in DB
                vendor = c["vendor"][0]
            k = (vendor, c["part_no"])
            if k in data:
                data[k][1] += 1
            else:
                data[k] = [c["description"], 1]
        data = sorted(((k[0], k[1], data[k][0], data[k][1]) for k in data), key=lambda x: -x[3])
        return self.from_dataset(
            title=self.title,
            columns=[
                "Vendor",
                "Part No",
                "Description",
                TableColumn("Count", format="numeric", align="right", total="sum"),
            ],
            data=data,
        )
