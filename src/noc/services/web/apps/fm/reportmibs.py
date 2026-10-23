# ---------------------------------------------------------------------
# MIBs Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.simplereport import SimpleReport, TableColumn
from noc.fm.models.mib import MIB
from noc.fm.models.mibdata import MIBData
from noc.core.translation import ugettext as _


class ReportreportMIBs(SimpleReport):
    title = _("Installed MIBs")

    def get_data(self, request: HttpRequest, **kwargs):
        data = []  # Mib, Last Updated, Entries, Depends, Used by
        for m in MIB.objects.order_by("name"):
            ec = MIBData.objects.filter(mib=m.id).count()
            data.append(
                [
                    m.name,
                    m.last_updated,
                    ec,
                    ", ".join(m.depends_on),
                    ", ".join([x.name for x in m.depended_by]),
                ]
            )
        return self.from_dataset(
            title=self.title,
            columns=[
                TableColumn("MIB", total_label="Total:"),
                TableColumn("Last Updated", format="date"),
                TableColumn("Entries", align="right", format="integer", total="sum"),
                TableColumn("Depends on"),
                TableColumn("Used by"),
            ],
            data=data,
            enumerate=True,
        )
